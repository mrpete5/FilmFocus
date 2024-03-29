"""
Name of code artifact: views.py
Brief description: Contains view functions for the FilmFocus web application, responsible for handling HTTP requests and rendering appropriate templates.
Programmer’s name: Mark
Date the code was created: 09/17/2023
Dates the code was revised: 03/26/2024
Brief description of each revision & author: Initialized view functions for various pages (Mark)
Preconditions: Django environment must be set up correctly. The services module must be available and correctly set up.
Acceptable and unacceptable input values or types: Functions expect HTTP requests as input.
Postconditions: Functions return rendered HTML templates as HttpResponse objects.
Return values or types: HttpResponse objects with rendered HTML content.
Error and exception condition values or types that can occur: Errors can occur if there are issues with the templates or if the services module encounters an error.
Side effects: Some functions may trigger database modifications via the services module.
Invariants: None.
Any known faults: None.
"""

from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, Http404
from django.contrib import messages
from .models import Movie, Watchlist, WatchlistEntry, UserProfile, MovieRating
from django.core.exceptions import ObjectDoesNotExist
from .forms import (
    NewUserForm,
    CustomAuthForm,
    NewWatchlistForm,
    PasswordResetForm,
    PasswordResetConfirmForm,
    WatchlistFilterForm,
    CatalogFilterForm,
    RatingForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout, authenticate, get_user_model, password_validation
import json
import re
import webapp.password_reset as pass_reset
from django.utils.http import urlsafe_base64_decode
from .services import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
import concurrent.futures
import random
import webbrowser



# Constants
RECOMMENDED_MOVIES_COUNT = 12


# View function for the index/home page
def index(request):
    ''' Handles the FilmFocus homepage. '''
    
    context = get_movies_for_index()
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
        context['watchlists'] = Watchlist.objects.filter(user=user)
            
    if request.method == 'POST':
        form = NewWatchlistForm(request.POST)
        if form.is_valid():
            watchlist_name = form.save()
            watchlist_name = form.cleaned_data.get('watchlist_name')
            create_watchlist(request, watchlist_name=watchlist_name)
            messages.success(request, f"You created a new watchlist named: {watchlist_name}!")

            # Redirect to the homepage on successful sign up
            return redirect('index')
        else:
            messages.error(request, "Watchlist creation failed")            
    else:
        form = NewWatchlistForm()
        
    context['watchlist_form'] = form
    return render(request, 'index.html', context)


# View function for the catalog page
def catalog(request):
    context = {}
    context['full_catalog'] = Movie.objects.all()
    context["genres"] = Genre.objects.all()
    context["streamers"] = StreamingProvider.objects.filter(name__in=filtered_providers)

    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)

    form = CatalogFilterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # Get filter items for context
            genre_ids = [int(genre) for genre in form.cleaned_data.get("genre").split()]
            context['filter_genre'] = Genre.objects.filter(pk__in=genre_ids) if genre_ids else None
            streamer_ids = [int(streamer) for streamer in form.cleaned_data.get("streaming_provider").split()]
            context['filter_streamer'] = StreamingProvider.objects.filter(pk__in=streamer_ids) if streamer_ids else None
            context['filter_year_begin'] = form.cleaned_data.get("year_begin")
            context['filter_year_end'] = form.cleaned_data.get("year_end")
            context['filter_imdb_begin'] = form.cleaned_data.get("imdb_begin")
            context['filter_imdb_end'] = form.cleaned_data.get("imdb_end")

            # Apply filter
            context['full_catalog'] = filter_movies(
                context.get('full_catalog'),
                context.get('filter_genre'),
                context.get('filter_streamer'),
                context.get('filter_year_begin'),
                context.get('filter_year_end'),
                context.get('filter_imdb_begin'),
                context.get('filter_imdb_end'))

            page_number = 1  # Get the page number from the request
            paginator = Paginator(context['full_catalog'], 120)  # 120 movies per page

            try:
                page_obj = paginator.page(page_number)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page

            context["page_obj"] = page_obj
            return render(request, 'catalog.html', context)
    
    # Use url query if it exist
    genre_ids = request.GET.get("genre")
    context['filter_genre'] = Genre.objects.filter(pk__in=genre_ids.split()) if genre_ids else context.get('full_genre')
    streamer_ids = request.GET.get("streaming_provider")
    context['filter_streamer'] = StreamingProvider.objects.filter(pk__in=streamer_ids.split()) if streamer_ids else context.get('filter_streamer')
    context['filter_year_begin'] = request.GET.get("year_begin")
    context['filter_year_end'] = request.GET.get("year_end")
    context['filter_imdb_begin'] = request.GET.get("imdb_begin")
    context['filter_imdb_end'] = request.GET.get("imdb_end")

    # Apply filter
    context['full_catalog'] = filter_movies(
        context.get('full_catalog'),
        context.get('filter_genre'),
        context.get('filter_streamer'),
        context.get('filter_year_begin'),
        context.get('filter_year_end'),
        context.get('filter_imdb_begin'),
        context.get('filter_imdb_end'))

    page_number = request.GET.get('page', 1)  # Get the page number from the request
    paginator = Paginator(context['full_catalog'], 120)  # 120 movies per page

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page

    context["page_obj"] = page_obj
    return render(request, 'catalog.html', context)


# View function for the movie details page
def movie_detail(request, movie_slug):
    ''' Handles the movie details pages where more information for a movie is all displayed. '''
    
    movie = get_object_or_404(Movie, slug=movie_slug)
    
    # Fetch recommended movies
    recommended_movies = movie.get_recommended_movies(RECOMMENDED_MOVIES_COUNT)
    rt_rating = None
    # Parse the Rotten Tomatoes rating to an integer
    try:
        rt_rating = int(movie.rotten_tomatoes_rating.split('%')[0])
    except (ValueError, AttributeError):
        pass
    
    # Determine which icon to use based on the Rotten Tomatoes rating
    movie.rt_icon = determine_rt_icon(rt_rating)
    
    if request.method == 'POST':
            form = NewWatchlistForm(request.POST)
            if form.is_valid():
                watchlist_name = form.save()
                watchlist_name = form.cleaned_data.get('watchlist_name')
                messages.success(request, f"You created a new watchlist named: {watchlist_name}!")

                # Redirect to the details on successful sign up
                return redirect('details')
            else:
                messages.error(request, "Watchlist creation failed")               
    else:
        form = NewWatchlistForm()

    context = {
        'movie': movie,
        'recommended_movies': recommended_movies
    }

    if request.user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)

    context['watchlist_form'] = form

    user = request.user
    if user.is_authenticated:
        context['watchlists'] = Watchlist.objects.filter(user=user)

    context['director_slugs'] = get_person_slugs(movie.director)
    context['director_names'] = get_person_names(movie.director)
    context['directors_pairs'] = zip(context['director_slugs'], context['director_names'])

    context['actor_slugs'] = get_person_slugs(movie.actors)
    context['actor_names'] = get_person_names(movie.actors)
    context['actors_pairs'] = zip(context['actor_slugs'], context['actor_names'])
    context['filmfocus_rating'] = get_filmfocus_rating(movie)
    return render(request, 'details.html', context)

# View function for the movie watchlists page
def watchlist(request, profile_name=None):
    if(profile_name is None):
        return redirect(reverse('login') + '?next=' + 'watchlist/')
    user = request.user
    context = {}
    profile = UserProfile.objects.get(user__username=profile_name)
    context['is_self'] = False

    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
        context['is_self'] = (user == profile.user)
        # Get watchlists
        if context['is_self']:
            watchlists = Watchlist.objects.filter(user=user)
            context['username'] = user.username
        else:
            watchlists = Watchlist.objects.filter(user=profile.user, is_private=False)
            context['username'] = profile_name
        
        # Only show the 'All' watchlist menu option if there are multiple watchlists
        context["multiple_watchlists"] = False
        watchlist_count = watchlists.count()
        if watchlist_count > 1:
            context["multiple_watchlists"] = True

        # Process new watchlist form that occurs when user doesnt have any watchlists
        if request.method == 'POST':
            form = NewWatchlistForm(request.POST or None)
            if form.is_valid():
                watchlist_name = form.cleaned_data.get("watchlist_name")
                create_watchlist(request, watchlist_name)

                # Redirect to watchlist page
                return redirect("watchlist")

        # TODO If no watchlists
        if not watchlists:
            # Setup Context for the frontend
            context['filter_watchlist'] = None
            context['filter_genre'] = None
            context['filter_streamer'] = None
            context['filter_year_begin'] = None
            context['filter_year_end'] = None
            context['filter_imdb_begin'] = None
            context['filter_imdb_end'] = None
            context['movie_list'] = None
            return render(request, "watchlist.html", context)

        context['watchlists'] = watchlists

        # TODO this might be temporary depending on how we want to implement the watchlist page
        if watchlists:
            form = WatchlistFilterForm(request.POST or None)
            if request.method == 'POST':
                if form.is_valid():
                    # Get The filter items 
                    genre_data = form.cleaned_data.get("genre")
                    if genre_data == 'None':
                        genre_data = ''
                    genre_ids = [int(genre) for genre in genre_data.split() if genre]
                    genre = Genre.objects.filter(pk__in=genre_ids) if genre_ids else None
                    streamer_data = form.cleaned_data.get("streaming_provider")
                    if streamer_data == 'None':
                        streamer_data = ''
                    streamer_ids = [int(streamer) for streamer in streamer_data.split() if streamer]
                    streamer = StreamingProvider.objects.filter(pk__in=streamer_ids) if streamer_ids else None
                    year_begin = form.cleaned_data.get("year_begin")
                    year_end = form.cleaned_data.get("year_end")
                    imdb_begin = form.cleaned_data["imdb_begin"]
                    imdb_end = form.cleaned_data["imdb_end"]
                    watchlist_id = form.cleaned_data.get("watchlist_id")

                    if context["is_self"]:
                        all_watchlists = Watchlist.objects.filter(user=user)
                    else:
                        all_watchlists = Watchlist.objects.filter(user=profile.user, is_private=False)

                    # Get the movie_list and handle watchlist_all
                    movie_list = Movie.objects.none()
                    if watchlist_id == "watchlist_all":
                        context['all_watchlist'] = True
                        for watchlist in all_watchlists:
                            movie_list |= Movie.objects.filter(watchlistentry__watchlist=watchlist).distinct()
                    else:
                        watchlist_id_int = int(watchlist_id)
                        watchlist = Watchlist.objects.get(pk=watchlist_id_int)
                        movie_list = Movie.objects.filter(watchlistentry__watchlist=watchlist)

                    # Excludes genre or streaming provider options that don't exist in the movie_list
                    context["genres"] = Genre.objects.all().filter(movies__in=movie_list).distinct()
                    context["streamers"] = StreamingProvider.objects.all().filter(movies__in=movie_list).distinct()

                    # Apply filter
                    movie_list = filter_movies(movie_list, genre, streamer, year_begin, year_end, imdb_begin, imdb_end)

                    # Setup Context for the frontend
                    context['filter_watchlist'] = watchlist
                    context['filter_genre'] = genre
                    context['filter_streamer'] = streamer
                    context['filter_year_begin'] = year_begin
                    context['filter_year_end'] = year_end
                    context['filter_imdb_begin'] = imdb_begin
                    context['filter_imdb_end'] = imdb_end
                    context['movie_list'] = movie_list
                    return render(request, "watchlist.html", context)
                # print("Form Errors:", form.errors) # Prints any error with a form submission
        # Setup Context for the frontend
        context['filter_watchlist'] = watchlists[0]
        context['movie_list'] = Movie.objects.filter(watchlistentry__watchlist=watchlists[0])
        context["genres"] = Genre.objects.all().filter(movies__in=context['movie_list']).distinct()
        context["streamers"] = StreamingProvider.objects.all().filter(movies__in=context['movie_list']).distinct()
        return render(request, "watchlist.html", context)
    return redirect('login')

# View function to process search results
def searchBar(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
        context['watchlists'] = Watchlist.objects.filter(user=user)
            
    if request.method == 'POST':
        form = NewWatchlistForm(request.POST)
        if form.is_valid():
            watchlist_name = form.save()
            watchlist_name = form.cleaned_data.get('watchlist_name')
            create_watchlist(request, watchlist_name=watchlist_name)
            messages.success(request, f"You created a new watchlist named: {watchlist_name}!")

            # Redirect to the homepage on successful sign up
            return redirect('index')
        else:
            messages.error(request, "Watchlist creation failed")               
    else:
        form = NewWatchlistForm()
    
    context['watchlist_form'] = form
    if request.method == 'GET':
        query = request.GET.get('query')
        context['query'] = query
        if query:
            if query[0] == '@':     # Search for a FilmFocus user
                username = query[1:]  # Remove the '@' symbol
                users = User.objects.filter(username__icontains=username)
                userProfiles = UserProfile.objects.filter(user__in=users).exclude(user=request.user)
                context['searchedUsers'] = userProfiles
                if user.is_authenticated: 
                    context['self_profile'] = UserProfile.objects.get(user=request.user)
                return render(request, 'user_results.html', context)
            
            elif query[0:6] == 'movie:':    # Fetch a movie from TMDb
                shift = 6
                if query[6] == ' ':         # If there is a space after the 'movie:' prefix
                    shift += 1
                movie_title = query[shift:]     # Remove the 'movie:' prefix
                context['query'] = movie_title  
                search_and_fetch_movie_by_title(movie_title)
                movies = Movie.objects.filter(title__icontains=movie_title)
                context['searchedMovies'] = movies
                return render(request, 'results.html', context)
            
            elif query[0:6] == 'actor:':
                shift = 6
                if query[6] == ' ':
                    shift += 1
                actor_name = query[shift:]
                actor_slug_list = get_person_slugs(actor_name)
                actor_slug = actor_slug_list[0]

                person_id = get_person_id(actor_name)
                if person_id:
                    tmdb_ids = get_actor_movies_from_tmdb_to_fetch(person_id)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        executor.map(search_and_fetch_movie_by_id, tmdb_ids)
                return redirect('actor', actor_slug)

            elif query[0:9] == 'director:':
                shift = 9
                if query[9] == ' ':
                    shift += 1
                director_name = query[shift:]
                director_slug_list = get_person_slugs(director_name)
                director_slug = director_slug_list[0]
                
                person_id = get_person_id(director_name)
                if person_id:
                    tmdb_ids = get_director_movies_from_tmdb_to_fetch(person_id)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        executor.map(search_and_fetch_movie_by_id, tmdb_ids)
                return redirect('director', director_slug)
            
            else:
                movies = Movie.objects.filter(title__icontains=query)
                context['searchedMovies'] = movies
                return render(request, 'results.html', context)
        else:
            print("No Info to show")
            return render(request, 'results.html', context)
        
# View function for getting asynchronous search results in real time
def searchbar(request, query):
    if request.method == 'GET':
        movies = Movie.objects.filter(title__icontains=query)[:5] # Quantity of movies in the searchbar query list
        return render(request, "searchbar.html", {"movies":movies})

# View function for getting movie watchlist popup
def popup(request, movie_id):
    context = {}
    if request.method == 'GET':
        if request.user.is_authenticated:
            context["watchlists"] = Watchlist.objects.filter(user=request.user)
        context["movie"] = Movie.objects.get(pk=movie_id)
        context["movie_in_watchlists"] = Watchlist.objects.filter(entries__movie=context["movie"]).distinct()
        return render(request, "popup.html", context)

# View function for getting help menu popup
def popup_help(request):
    context = {}
    if request.method == 'GET':
        context["instructions"] = "This is the help menu. It will contain instructions on\
                                    how to use the website. Create tabs/buttons for each topic \
                                    around here near the top and dynamically display\
                                    information below."
        context["self_doubt"] = "Or is this a dumb idea as a popup and should just be the FAQ page?"
        return render(request, "popup_help.html", context)

# View function for getting user movie rating popup
def popup_rating(request, movie_id):
    context = {}
    if request.method == 'GET':
        movie = Movie.objects.get(pk=movie_id)
        context["movie"] = movie
        context["rating_exists"] = False
        context["user_rating"] = None
        if request.user.is_authenticated:
            user = request.user

            # check and update already existing entry
            query = MovieRating.objects.filter(user=user, movie=movie)
            context["rating_exists"] = query.exists()
            if context["rating_exists"]:
                context["user_rating"] = query.first().user_rating

        return render(request, "popup_rating.html", context)


# View function for the Watchlist random movie selection popup
def popup_select_movie(request, watchlist_id):
    context = {}
    if request.method == 'GET':
        user = request.user
        all_watchlists = Watchlist.objects.filter(user=user)

        watchlist_movies = Movie.objects.none()  # Initialize an empty queryset
        if watchlist_id == 9999:    # 9999 is the default watchlist id for all watchlist
            context['all_watchlist'] = True
            for watchlist in all_watchlists:
                watchlist_movies |= Movie.objects.filter(watchlistentry__watchlist=watchlist).distinct()
        else:
            watchlist_id_int = int(watchlist_id)
            watchlist = Watchlist.objects.get(pk=watchlist_id_int)
            watchlist_movies = Movie.objects.filter(watchlistentry__watchlist=watchlist)

        genre_ids = [int(genre) for genre in request.GET.get("genre").split()]
        genre = Genre.objects.filter(pk__in=genre_ids) if genre_ids else None
        streamer_ids = [int(streamer) for streamer in request.GET.get("streaming_provider").split()]
        streamer = StreamingProvider.objects.filter(pk__in=streamer_ids) if streamer_ids else None
        year_begin = request.GET.get('year_begin')
        year_end = request.GET.get('year_end')
        imdb_begin = request.GET.get('imdb_begin')
        imdb_end = request.GET.get('imdb_end')

        filtered_movies = filter_movies(watchlist_movies, genre, streamer, year_begin, year_end, imdb_begin, imdb_end)
        movies = random.sample(list(filtered_movies), min(len(filtered_movies), 3))
        context['movies'] = movies

    return render(request, "popup_select_movie.html", context)

# View function for the Catalog random movie selection popup
def popup_catalog_select(request):
    context = {}
    if request.method == 'GET':
        movies = Movie.objects.all()

        genre_ids = [int(genre) for genre in request.GET.get("genre").split()]
        genre = Genre.objects.filter(pk__in=genre_ids) if genre_ids else None
        streamer_ids = [int(streamer) for streamer in request.GET.get("streaming_provider").split()]
        streamer = StreamingProvider.objects.filter(pk__in=streamer_ids) if streamer_ids else None
        year_begin = request.GET.get('year_begin')
        year_end = request.GET.get('year_end')
        imdb_begin = request.GET.get('imdb_begin')
        imdb_end = request.GET.get('imdb_end')

        movies = filter_movies(movies, genre, streamer, year_begin, year_end, imdb_begin, imdb_end).order_by('?')[:3]

        context['movies'] = movies

    return render(request, "popup_catalog_select.html", context)

# View function for the about page
def about(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
    return render(request, "about.html", context)

# View function for the user profile page
def profile(request, profile_name):
    context = {}
    profile = UserProfile.objects.get(user__username=profile_name)

    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
        context['is_self'] = (user == profile.user)
    else:
        context['is_self'] = False

    context['user_profile'] = profile

    if context['is_self']:
        context['watchlists'] = Watchlist.objects.filter(user=profile.user)
        context['friend_requests'] = FriendRequest.objects.filter(Q(to_user__user=request.user) | Q(from_user__user=request.user))
        context['movie_ratings_count'] = MovieRating.objects.filter(user=user).count()
    else:
        context['watchlists'] = Watchlist.objects.filter(user=profile.user, is_private=False)
        context['movie_ratings_count'] = MovieRating.objects.filter(user=profile.user).count()

    return render(request, "userprofile.html", context)


# View function for getting the profile edit popup
@login_required
def edit_profile_popup(request):
    context = {}
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            context["user_profile"] = user_profile
            context["biography"] = user_profile.biography if user_profile.biography else ""
        return render(request, "popup_profile_edit.html", context)

# View function for updating profile information
@login_required
def save_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        data = json.loads(request.body)

        bio_text = data.get('biography')
        profile_pic = data.get('profile_pic')

        user_profile.biography = bio_text
        if profile_pic:
            user_profile.profile_pic = profile_pic
        user_profile.save()

        return JsonResponse({'status': 'success', 'message': 'Profile saved successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# View function for friend request page
@login_required
def friend_requests(request):
    context={}
    if request.user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
        context["in_requests"] = FriendRequest.objects.filter(to_user__user=request.user)
        context["out_requests"] = FriendRequest.objects.filter(from_user__user=request.user)
        return render(request, "friend_requests.html", context)
    
@login_required
@require_POST
def create_friend_request(request, to_id):
    try:
        if request.user.is_authenticated:
            user = UserProfile.objects.get(user=request.user)
            friend = UserProfile.objects.get(pk=to_id)
            friend_request = FriendRequest.objects.create(from_user=user, to_user=friend)
            friend_request.save()
            return JsonResponse({'status': 'success', 'message': 'Friend request created'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
# View function for accepting a friend request
@login_required
@require_POST
def accept_friend_request(request, from_id):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user=request.user)
        friend = UserProfile.objects.get(pk=from_id)

        user.friends.add(friend)
        friend.friends.add(user)
        
        FriendRequest.objects.get(from_user=friend, to_user=user).delete()
    return redirect("friend_requests")

# View function for rejecting a friend request
@login_required
@require_POST
def reject_friend_request(request, from_id):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user=request.user)
        friend = UserProfile.objects.get(pk=from_id)

        user.friends.remove(friend)
        friend.friends.remove(user)

        # Handle bi-directional friend requests
        try:
            FriendRequest.objects.get(from_user=user, to_user=friend).delete()
        except:
            FriendRequest.objects.get(from_user=friend, to_user=user).delete()
    return redirect("friend_requests")

# View function for removing a friend
@login_required
@require_POST
def remove_friend(request, friend_id):
    try:
        if request.user.is_authenticated:
            user = UserProfile.objects.get(user=request.user)
            friend = UserProfile.objects.get(pk=friend_id)

            user.friends.remove(friend)
            friend.friends.remove(user)
            return JsonResponse({'status': 'success', 'message': 'Friend removed'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# View function for the 404 error page
def four04(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
    return render(request, "404.html", context)

# View function to create a movie rating
# TODO: utilize has_watched
@login_required
@require_POST
def create_rating(request, movie_id, rating) :
    if request.user.is_authenticated:
        # check bounds
        if rating > 10 or rating < 0:
            return JsonResponse({'status': 'error', 'error': 'out of bounds'}, status=405)

        # get user and movie objects
        user = request.user
        movie = Movie.objects.get(pk=movie_id)

        # check and update already existing entry
        query = MovieRating.objects.filter(user=user, movie=movie)
        if query.exists():
            movie_rating = query.first()
            movie_rating.user_rating = rating
            movie_rating.save()
            return JsonResponse({'status': 'success', "message": "movie rating updated"})

        # otherwise create new entry
        movie_rating = MovieRating.objects.create(user=user, movie=movie, user_rating=rating, has_watched=True)
        movie_rating.save()
        return JsonResponse({'status': 'success', "message": "movie rating created"})
    return JsonResponse({'status': 'error', 'error': 'illegal request'}, status=405)

# View function to remove a movie rating
@login_required
@require_POST
def remove_rating(request, movie_id) :
    if request.user.is_authenticated:
        # get user and movie object
        user = request.user
        movie = Movie.objects.get(pk=movie_id)
        
        # delete if movie rating exists
        movie_ratings = MovieRating.objects.filter(user=user, movie=movie)
        if not movie_ratings.exists():
            return JsonResponse({'status': 'error', 'error': 'rating does not exist'}, status=405)
        movie_ratings.delete()

        return JsonResponse({'status': 'success', "message": "movie rating removed"})
    return JsonResponse({'status': 'error', 'error': 'illegal request'}, status=405)


# View function for the password reset page
def pwreset(request):
    form = PasswordResetForm(request.POST or None)
    if request.method == "POST":
        # Define form information
        try:
            if form.is_valid():
                # get user using username from form
                username = form.cleaned_data.get("username")
                user = User.objects.get(username=username)

                # Send Email
                pass_reset.send_email(request, user)

                # TODO redirect to email sent page
                return redirect("index")
            else:
                raise Exception("Invalid Form")
        # post error message
        except ObjectDoesNotExist:
            form.add_error(None, "User Could not be Found or Doesn't Exist")
        except Exception as e:
            form.add_error(None, e)
    return render(request, "pwreset.html", {"form": form})

# View definition for password comfirmation page
def pwresetconfirm(request, uidb64, token):
    try:
        # get uid and user information
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(get_user_model(), pk=uid)

        # error if uidb64 or token failure
        if user == None or not default_token_generator.check_token(user, token):
            raise Exception("Invalid Reset Link")
    except Exception as e:
        # TODO change to redirect to 404 or failed page
        return redirect("index")

    # Define form information
    form = PasswordResetConfirmForm(request.POST or None)
    if request.method == "POST":
        try:
            if form.is_valid():
                    # get password details from form
                    new_password_1 = form.cleaned_data.get("new_password_1")
                    new_password_2 = form.cleaned_data.get("new_password_2")

                    # errors if something is wrong with password inputs
                    password_validation.validate_password(new_password_1)
                    if new_password_1 != new_password_2:
                        raise Exception("Passwords do not match")

                    # otherwise change the password
                    pass_reset.change_password(user, new_password_1)

                    # TODO redirect to a password change comfirmation page
                    return redirect("login")
            else:
                raise Exception("Invalid Form")
        # post error message
        except Exception as e:
            form.add_error(None, e)
    return render(request, "pwresetconfirm.html", {"form": form})

'''
# View function for the login page
# Uses 'login_user' view function and 'login.html'
# If view function named login, then conflicts with Django built-in login function, if view function named login
'''
def login_user(request):
    # First define the form 
    form = CustomAuthForm(data=request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            
            # Get user after validating form 
            user = form.get_user()  
            username = form.cleaned_data.get('username')
            
            # Check if user has profile
            if not hasattr(user, 'userprofile'):
                UserProfile.objects.get_or_create(user=user)
            
            # Login user
            login(request, user)

            # Rest of login logic
            messages.info(request, f"Hello {username}, welcome back!")
            redirect_page = reverse('index')
            next_page = request.GET.get('next')
            # Resolve the URL using the 'next' parameter value
            # Check if the redirect_page is not None
            if next_page == 'watchlist/':
                # Add the user profile to the end of the redirect_page URL
                profile = UserProfile.objects.get(user__username=user)
                redirect_page += next_page
                redirect_page += f'{profile}/'
                print(redirect_page)
                return redirect(redirect_page)
            return redirect('index')
            
        else:
            messages.error(request, "Invalid username or password")
            form.add_error("username", "Invalid username or password")

    else:
        form = CustomAuthForm()

    return render(
        request=request,
        template_name="login.html",
        context={"login_form": form}
    )

''' # Redirect to the index page
    # OR 
    # Render the logout page (current)
    # - Need to pick which one
'''
# View function for the logout page
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    # return redirect('index')              
    return render(request, "logout.html")  


# View function for the signup page
def signup(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user) # Create UserProfile instance for the new user
            login(request, user)
            username = form.cleaned_data.get('username')
            messages.success(request, f"You created a new account for {username}!")
            messages.success(request, f"You are now logged in as {username}!")
            
            # Redirect to the homepage on successful sign up
            return redirect('index')
        else:
            messages.error(request, "Registration failed")
            messages.error(request, "Fill out all fields")
            messages.error(request, "Please try again")

    else:
        form = NewUserForm()
    return render(request=request, template_name="signup.html", context={"register_form":form})


# View function for the FAQ page
def faq(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)
    return render(request, "faq.html", context)


@login_required
@require_POST
def create_watchlist(request, watchlist_name):
    try:
        watchlist = Watchlist.objects.create(user=request.user, watchlist_name=watchlist_name)
        watchlist.save()
        return JsonResponse({'status': 'success', 'message': 'Watchlist created'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# View function for getting the delete watchlist confirmation popup
@login_required
def delete_watchlist_popup(request, watchlist_id, watchlist_name):
    context = {}
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            context["user_profile"] = user_profile
            context["watchlist_id"] = watchlist_id
            context["watchlist_name"] = watchlist_name
        return render(request, "popup_del_wlist.html", context)

@login_required
@require_POST
def remove_watchlist(request, watchlist_id):
    try:
        watchlist = Watchlist.objects.get(user=request.user, pk=watchlist_id)
        watchlist_entries = WatchlistEntry.objects.filter(watchlist=watchlist)
        for entry in watchlist_entries:
            entry.delete()
        watchlist.delete()
        return JsonResponse({'status': 'success', 'message': 'Watchlist removed'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def add_to_watchlist(request, watchlist_id, movie_id):
    try:
        watchlist = Watchlist.objects.get(pk=watchlist_id, user=request.user)
        movie = Movie.objects.get(pk=movie_id)
        new_watchlist_entry = WatchlistEntry(
            watchlist = watchlist,
            movie = movie,
        )
        new_watchlist_entry.save()
        return JsonResponse({'status': 'success', 'message': 'Movie added to watchlist'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def remove_from_watchlist(request, watchlist_id, movie_id):
    try:
        watchlist = Watchlist.objects.get(pk=watchlist_id, user=request.user)
        movie = Movie.objects.get(pk=movie_id)
        watchlist_entry = WatchlistEntry.objects.get(watchlist=watchlist, movie=movie)
        watchlist_entry.delete()
        return JsonResponse({'status': 'success', 'message': 'Movie removed from watchlist'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def toggle_watchlist_privacy(request, watchlist_id):
    try:
        watchlist = Watchlist.objects.get(pk=watchlist_id, user=request.user)
        if(watchlist.is_private == True):
            watchlist.is_private = False
            responseString = "Privacy changed to public"
        elif(watchlist.is_private == False):
            watchlist.is_private = True
            responseString = "Privacy changed to private"
        watchlist.save()
        return JsonResponse({'status': 'success', 'message': responseString})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
# View function for user movie ratings
def rating(request, profile_name):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)

    user = get_object_or_404(User, username=profile_name)
    movie_ratings = MovieRating.objects.filter(user=user).select_related('movie').order_by(F('id').desc())
    context['user_name'] = profile_name
    context['movie_ratings'] = movie_ratings

    form = RatingForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # Get filter items for context
            context['filter_rating_begin'] = form.cleaned_data["rating_begin"]
            context['filter_rating_end'] = form.cleaned_data["rating_end"]
            
            # Apply filter
            context['movie_ratings'] = filter_ratings(context['movie_ratings'], 
                                                      context['filter_rating_begin'], 
                                                      context['filter_rating_end'])

            paginator = Paginator(context['movie_ratings'], 120)  # 120 movies per page
            try:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page
            context["page_obj"] = page_obj

            return render(request, 'rating.html', context)

    paginator = Paginator(movie_ratings, 120)  # 120 movies per page

    page_number = request.GET.get('page', 1)  # Get the page number from the request
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page

    context["page_obj"] = page_obj

    return render(request, 'rating.html', context)

# View function for the directors pages
def director(request, director_name):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)

    director_name = re.sub(r'(?<!-)-(?!-)', ' ', director_name)   # Handles single hypen into space
    if "--" in director_name:
        director_name = director_name.replace("--", "-")          # Handles double hypen into single hyphen
        
    context['director_name'] = director_name
    context['movies'] = get_movies_by_director(director_name)

    return render(request, "director.html", context)

# View function for the actors pages
def actor(request, actor_name):
    context = {}
    user = request.user
    if user.is_authenticated:
        context['logged_in_user_profile_picture'] = get_logged_in_user_profile_picture(request)

    actor_name = re.sub(r'(?<!-)-(?!-)', ' ', actor_name)   # Handles single hypen into space
    if "--" in actor_name:
        actor_name = actor_name.replace("--", "-")          # Handles double hypen into single hyphen
    
    context['actor_name'] = actor_name

    person_id = get_person_id(actor_name)
    if person_id:
        context['movies'] = get_movies_from_tmdb_by_actor(person_id)
    else:
        context['movies'] = get_movies_by_actor(actor_name)

    return render(request, "actor.html", context)


# View function for getting refreshed movie data for a specific movie
def refresh_movie_data(request, tmdb_id):
    try:
        get_refreshed_movie_data(tmdb_id)
        return JsonResponse({'status': 'success', 'message': 'Movie data updated.'})
    except Movie.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Movie not found.'})


# Test page that displays posters for potential movie banning
def testforban(request):
    start_date = "2023-01-01"  # Range of movies to display
    end_date = "2024-12-31"
    view_jw_nulls = False

    limit_quantity = True
    fetch_movies_count = 25
    start_object = 1175
    end_object = start_object + fetch_movies_count
    if limit_quantity:
        movies_to_display = list(Movie.objects.all()[start_object:end_object])
    
    if view_jw_nulls:
        # Get all Movie objects
        movies = Movie.objects.all()
        
        # Filter movies where justwatch_url is None, tmdb_id matches, and runtime is not 0
        movies_to_display = [
            movie for movie in movies 
            if movie.justwatch_url is None and movie.runtime != 0
        ]
    else:
        # If not viewing movies with justwatch_url=None, use the original function
        movies_to_display = handle_test_for_ban(start_date, end_date)
    
    return render(request, "testforban.html", {"movies": movies_to_display})


# Test page that displays selected movie attribute data
def testdisplay(request):
    movies_to_display = handle_test_display_page(fetch_movies_count=10)
    return render(request, "testdisplay.html", {"movies": movies_to_display})

# Helper function to update JustWatch or Letterboxd URLs
def update_webscraper_url(request, movie_id):
    if request.method == 'POST':
        url_to_update = request.POST.get('true_webscraper_url')
        is_letterboxd_url = "letterboxd.com" in url_to_update
        is_justwatch_url = "justwatch.com" in url_to_update
        try:
            movie = Movie.objects.get(id=movie_id)
            if is_justwatch_url:
                # Update JustWatch URL
                movie.justwatch_url = url_to_update
                movie.save()
                print(f"JustWatch URL updated for movie '{movie.title}': {url_to_update}")
            elif is_letterboxd_url:
                # Update Letterboxd URL
                movie.letterboxd_url = url_to_update
                movie.save()
                update_letterboxd_ratings(update_movie=movie)
                print(f"Letterboxd URL updated for movie '{movie.title}': {url_to_update}")
            
        except Movie.DoesNotExist:
            print(f"Movie with ID {movie_id} not found.")

    return redirect('testwebscraper')


# Test page for getting JustWatch or Letterboxd URL for web scraping
def testwebscraper(request):
    letterboxd_scraper = True       # Use Letterboxd scraper instead of JustWatch
    include_known_lbd_urls = True   # Include movies with known Letterboxd URLs
    include_known_jw_urls = False   # Include movies with known JustWatch URLs
    include_2024 = True
    limit_quantity = True
    fetch_movies_count = 25
    start_object = 1400              # Letterboxd checked through 1400
    end_object = start_object + fetch_movies_count
    if limit_quantity:
        movies_to_display = list(Movie.objects.all()[start_object:end_object])
    else:
        movies_to_display = list(Movie.objects.all())

    def generate_jw_url(title):
        formatted_title = '+'.join(title.split())
        return f"https://www.justwatch.com/us/search?q={formatted_title}"
    
    def generate_lbd_url(title):
        whitelist_char = [' ', '-']
        hyphenated_title = ''.join(char if char.isalnum() or char in whitelist_char else '' for char in title)
        hyphenated_title = hyphenated_title.replace(' ', '-').replace('\t', '-').replace('\n', '-').replace('\r', '-')
        hyphenated_title = "-".join(filter(None, hyphenated_title.split("-")))
        hyphenated_title = hyphenated_title.lower()
        return f"https://letterboxd.com/csi/film/{hyphenated_title}/rating-histogram"
    
    def convert_to_rating_histogram_url(letterboxd_url):
        if letterboxd_url:
            start_index = letterboxd_url.find("film/") + len("film/")
            end_index = letterboxd_url.find("/rating-histogram")
            if start_index != -1 and end_index != -1:  # Check if both "film/" and "/rating-histogram" are found
                movie_title = letterboxd_url[start_index:end_index]
                return f"https://letterboxd.com/film/{movie_title}/members/rated/.5-5/"
        return None

    if letterboxd_scraper: # Letterboxd
        # Filter movies based on include_known_lbd_urls
        if not include_known_lbd_urls:
            # Exclude movies with known Letterboxd URLs
            movies_to_display = [movie for movie in movies_to_display if movie.letterboxd_url is None]
            # Exclude movies released this year
            if not include_2024:
                movies_to_display = [movie for movie in movies_to_display if movie.release_year != 2024]
            # Generate Letterboxd search URL for movies with no Letterboxd URL
            for movie in movies_to_display:
                if not movie.letterboxd_url:
                    movie.letterboxd_url = generate_lbd_url(movie.title)
                    movie.search_url = f"https://letterboxd.com/search/{movie.title}/"
        else:
            for movie in movies_to_display:
                if movie.letterboxd_url:
                    movie.search_url2 = convert_to_rating_histogram_url(movie.letterboxd_url)
                    # webbrowser.open_new_tab(movie.search_url2)

    else:  # JustWatch
        # Filter movies based on include_known_jw_urls
        if not include_known_jw_urls:
            # Exclude movies "Not Found" on JustWatch
            movies_to_display = [movie for movie in movies_to_display if movie.justwatch_url != "Not Found"]
            # Exclude movies released this year
            if not include_2024:
                movies_to_display = [movie for movie in movies_to_display if movie.release_year != 2024]
            # Include movies with None or empty string for justwatch_url
            movies_to_display = [movie for movie in movies_to_display if movie.justwatch_url in [None, ""]]

            # Generate JustWatch search URL for movies with no JustWatch URL
            for movie in movies_to_display:
                if not movie.justwatch_url:
                    movie.justwatch_url = generate_jw_url(movie.title)

    print(f"Movie count: %d" % len(movies_to_display))
    context = {"movies": movies_to_display, "letterboxd_scraper": letterboxd_scraper}
    return render(request, "testwebscraper.html", context)