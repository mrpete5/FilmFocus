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
from django.http import JsonResponse, Http404
from django.contrib import messages
from .models import Movie, Watchlist, WatchlistEntry
from .forms import NewUserForm, CustomAuthForm
from django.contrib.auth import login, logout, authenticate
import json

# Constants
RECOMMENDED_MOVIES_COUNT = 10

# from django.contrib.auth.forms import AuthenticationForm
# from django.http import HttpRequest 
from .services import *


# View function for the index/home page
def index(request):
    ''' Handles the FilmFocus homepage. '''
    
    context = get_movies_for_index()
    user = request.user
    if user.is_authenticated:
        context['watchlists'] = Watchlist.objects.filter(user=user)
        
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
    
    context = {
        'movie': movie,
        'recommended_movies': recommended_movies
    }
    
    return render(request, 'details.html', context)


# Determines the Rotten Tomatoes icon based on the Rotten Tomatoes rating
def determine_rt_icon(rt_rating):
    if rt_rating is not None:
        if rt_rating >= 75:
            return 'img/logos/Rotten_Tomatoes_certified_fresh.png'
        elif rt_rating >= 60:
            return 'img/logos/Rotten_Tomatoes_fresh.png'
        else:
            return 'img/logos/Rotten_Tomatoes_rotten.png'
    return None

# View function for the movie watchlists page
def watchlist(request):
    return render(request, "watchlist.html")

# View function for the about page
def about(request):
    return render(request, "about.html")

# View function for the 404 error page
def four04(request):
    return render(request, "404.html")

# View function for the password reset page
def pwreset(request):
    return render(request, "pwreset.html")


'''
# View function for the login page
# Uses 'login_user' view function and 'login.html'
# If view function named login, then conflicts with Django built-in login function, if view function named login
'''
def login_user(request):
    if request.method == 'POST':
        form = CustomAuthForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password')                  # do not delete before 11/01, might need to change
            # user = authenticate(username=username, password=password)     # do not delete before 11/01, might need to change
            if user is not None:
                login(request, user)
                messages.info(request, f"Hello {username}, welcome back!")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = CustomAuthForm()                                 
        
    return render(request=request, template_name="login.html", context={"login_form": form})


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


# Require user to be logged in to access this view
@login_required  
def add_movie_to_watchlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            movie_id = data.get('movie_id')
            watchlist_id = data.get('watchlist_id')
            movie = get_object_or_404(Movie, id=movie_id)
            watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
            
            # Check if the movie is already in the watchlist
            if not WatchlistEntry.objects.filter(watchlist=watchlist, movie=movie).exists():
                WatchlistEntry.objects.create(watchlist=watchlist, movie=movie)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Movie already in watchlist'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except KeyError:
            return JsonResponse({'success': False, 'error': 'Invalid data format'})
    else:
        raise Http404


# View function for the poster game page
def poster_game(request):
    ''' Play a poster reveal guessing game. '''
    # TODO: Implement this function to play a poster reveal guessing game.    
  
    movies_to_display = handle_poster_game(movie_count=1)
    return render(request, "postergame.html", {"movies": movies_to_display})


# Test page that displays posters for potential movie banning
def testforban(request):
    start_date = "2023-10-06"  # Adjusted start date
    end_date = "2023-12-30"    # Adjusted end date

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
    
    # Add all tests into settings list
    settings = [erase_movie_db,         # USE WITH CAUTION
                init_movie_db,
                get_now_playing,        
                update_streaming,       # Takes a while
                update_recs,            # Takes a while
                get_discover_movies,    # Takes a while
                update_letterboxd,      # Takes a while
                ]
  
    movies_to_display = handle_test_display_page(settings)
    return render(request, "testdisplay.html", {"movies": movies_to_display})
