"""
Name of code artifact: views.py
Brief description: Contains view functions for the FilmFocus web application, responsible for handling HTTP requests and rendering appropriate templates.
Programmer’s name: Mark
Date the code was created: 09/17/2023
Dates the code was revised: 10/05/2023
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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, Http404
from django.contrib import messages
from .models import Movie, Watchlist, WatchlistEntry, UserProfile
from django.core.exceptions import ObjectDoesNotExist
from .forms import (
    NewUserForm,
    CustomAuthForm,
    NewWatchlistForm,
    PasswordResetForm,
    PasswordResetConfirmForm,
    WatchlistFilterForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login, logout, authenticate, get_user_model, password_validation
import json
import webapp.password_reset as pass_reset
from django.utils.http import urlsafe_base64_decode
from .services import *


# Constants
RECOMMENDED_MOVIES_COUNT = 12


# View function for the index/home page
def index(request):
    ''' Handles the FilmFocus homepage. '''
    
    context = get_movies_for_index()
    user = request.user
    if user.is_authenticated:
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


# View function for the movie details page
def movie_detail(request, movie_slug):
    ''' Handles the movie details pages where more information for a movie is all displayed. '''
    
    movie = get_object_or_404(Movie, slug=movie_slug)
    
    # Fetch recommended movies
    # TODO: Implement this function to fetch Similar & Recommended from
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

    context['watchlist_form'] = form

    user = request.user
    if user.is_authenticated:
        context['watchlists'] = Watchlist.objects.filter(user=user)

    return render(request, 'details.html', context)

# View function for the movie watchlists page
def watchlist(request):
    user = request.user
    context = {}

    if user.is_authenticated:
        # Get watchlists
        watchlists = Watchlist.objects.filter(user=user)

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
                    # Get The watchlist Id from the form
                    watchlist_id = form.cleaned_data.get("watchlist_id")

                    # Get Selected Watchlist and Associated Movies in the Watchlist
                    watchlist = Watchlist.objects.get(pk=watchlist_id)
                    movie_list = Movie.objects.filter(watchlistentry__watchlist=watchlist)

                    # Excludes genre or streaming provider options that don't exist in the movie_list
                    context["genres"] = Genre.objects.all().filter(movies__in=movie_list).distinct()
                    context["streamers"] = StreamingProvider.objects.all().filter(movies__in=movie_list).distinct()

                    # Fitler for Genre
                    genre = Genre.objects.filter(name=form.cleaned_data["genre"]).first()
                    if genre:
                        movie_list = movie_list.filter(genres=genre)

                    # Filter for Streaming Providers
                    streamer = StreamingProvider.objects.filter(name=form.cleaned_data["streaming_provider"]).first()
                    if streamer:
                        movie_list = movie_list.filter(streaming_providers=streamer)

                    # Filter for release year
                    year_begin = form.cleaned_data["year_begin"]
                    year_end = form.cleaned_data["year_end"]
                    if year_begin and year_end:
                        movie_list = movie_list.filter(release_year__range=(year_begin, year_end))

                    # Filte for IMDB rating
                    imdb_begin = form.cleaned_data["imdb_begin"]
                    imdb_end = form.cleaned_data["imdb_end"]
                    # TODO imdb rating is a ChatField in the movie model and you can't range it
                    # if imdb_begin and imdb_end:
                    #     movie_list = movie_list.filter(imdb_rating__range=(imdb_begin, imdb_end))
                    
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
            if query[0] == '@':
                username = query[1:]  # Remove the '@' symbol
                users = User.objects.filter(username__icontains=username)
                userProfiles = UserProfile.objects.filter(user__in=users)
                context['searchedUsers'] = userProfiles
                if user.is_authenticated: 
                    context['self_profile'] = UserProfile.objects.get(user=request.user)
                return render(request, 'user_results.html', context)
            else:
                movies = Movie.objects.filter(title__icontains=query)
                context['searchedMovies'] = movies
                return render(request, 'results.html', context)
                # return render(request, 'results.html', 'searchedMovies': movies)
        else:
            print("No Info to show")
            return render(request, 'results.html', context)
        
# View function for getting asynchronous search results in real time
def searchbar(request, query):
    if request.method == 'GET':
        movies = Movie.objects.filter(title__icontains=query)[:4] # Quantity of movies in the searchbar query list
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


# View function for the about page
def about(request):
    return render(request, "about.html")

# View function for the user profile page
def profile(request, profile_name):
    context = {}
    profile = UserProfile.objects.get(user__username=profile_name)

    user = request.user
    if user.is_authenticated:
        context['is_self'] = (user == profile.user)
    else:
        context['is_self'] = False

    context['user_profile'] = profile

    if context['is_self']:
        context['watchlists'] = Watchlist.objects.filter(user=profile.user)
        context['friend_requests'] = FriendRequest.objects.filter(to_user__user=request.user)
    else:
        context['watchlists'] = Watchlist.objects.filter(user=profile.user, is_private=False)

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
    return render(request, "404.html")

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
    return render(request, "faq.html")


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


# Test page that displays posters for potential movie banning
def testforban(request):
    start_date = "2023-10-01"  # Range of movies to display
    end_date = "2023-12-30"

    movies_to_display = handle_test_for_ban(start_date, end_date)
    return render(request, "testforban.html", {"movies": movies_to_display})


# Test page that handles data fetch calls and displays movies
def testdisplay(request):
    # Always set these flags as False before committing changes
    erase_movie_db = False                # USE WITH CAUTION, erases all movie database contents
    init_movie_db = False                 # Performs Popular fetch from TMDB 
    get_now_playing = False               # Performs Now Playing fetch from TMDB
    update_streaming = False              # Updates all movie streaming providers from TMDB, takes a while
    update_recs = False                   # Updates all movie recommendations from TMDB, takes a while
    get_discover_movies = False           # Fetches all discover movies from TMDB, takes a while
    update_letterboxd = False             # Updates all movie letterboxd info from webscraper, takes a while
    get_specific_movie_by_search = False   # Fetches a specific movie 
    search_term = "Fight Club"            # If (get_specific_movie_by_search): Name of specific movie search   

    # Search for a specific movie from tmdb database with tmdb_id and data 
    #   from the master list found at FilmFocus\webapp\data\tmdb_master_movie_list.json
    # Attempt to search for a specific movie based on the movie tmdb_id or movie title.
    # search_and_fetch_movie_by_id(settings[tmdb_id_to_search_and_fetch]) # Alternative method, Attempt to search for a specific movie based on the movie tmdb_id.


    # Add all tests into settings list
    settings = [erase_movie_db,                     #  USE WITH CAUTION, settings[0],
                init_movie_db,                      # settings[1], Can take a while based on settings/quantities
                get_now_playing,                    # settings[2], Can take a while based on settings/quantities
                update_streaming,                   # settings[3], Takes a while, performed on entire FilmFocus movie database around 10 thousand movies
                update_recs,                        # settings[4], Takes a while, performed on entire FilmFocus movie database around 10 thousand movies
                get_discover_movies,                # settings[5], Takes a while, performed on entire FilmFocus movie database around 10 thousand movies
                update_letterboxd,                  # settings[6], Takes a while, performed on entire FilmFocus movie database around 10 thousand movies
                get_specific_movie_by_search,       # settings[7], Should be very fast but may be unsuccessful
                search_term,                        # settings[8], Passing a blank string for initialization purposes
                ]

    movies_to_display = handle_test_display_page(settings)
    return render(request, "testdisplay.html", {"movies": movies_to_display})