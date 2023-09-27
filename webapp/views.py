"""
Name of code artifact: views.py
Brief description: Contains view functions for the FilmFocus web application, responsible for handling HTTP requests and rendering appropriate templates.
Programmer’s name: Mark
Date the code was created: 09/17/2023
Dates the code was revised: 09/21/2023
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

from django.shortcuts import render, get_object_or_404
from .services import *

# View function for the index page
def index(request):
    context = get_movies_for_index()
    return render(request, 'index.html', context)

# View function for the movie details page
def movie_detail(request, movie_slug):
    movie = get_object_or_404(Movie, slug=movie_slug)
    
    # Parse the Rotten Tomatoes rating to an integer
    try:
        rt_rating = int(movie.rotten_tomatoes_rating.split('%')[0])
    except (ValueError, AttributeError):
        rt_rating = None
    
    # Determine which icon to use based on the Rotten Tomatoes rating
    if rt_rating is not None:
        if rt_rating >= 75:
            movie.rt_icon = 'img/logos/Rotten_Tomatoes_certified_fresh.png'
        elif rt_rating >= 60:
            movie.rt_icon = 'img/logos/Rotten_Tomatoes_fresh.png'
        else:
            movie.rt_icon = 'img/logos/Rotten_Tomatoes_rotten.png'
    else:
        movie.rt_icon = None
    
    return render(request, 'details.html', {'movie': movie})

# View function for the movie watchlists page
def watchlist(request):
    return render(request, "watchlist.html")

# View function for the about page
def about(request):
    return render(request, "about.html")

# View function for the 404 error page
def four04(request):
    return render(request, "404.html")

# View function for the sign-in page
def signin(request):
    return render(request, "signin.html")

# View function for the sign-up page
def signup(request):
    return render(request, "signup.html")

# View function for the FAQ page
def faq(request):
    return render(request, "faq.html")


# Test page that displays posters for potential movie banning
def testforban(request):
    start = 1       # Manually set start value
    end = 1000     # Manually set end value

    movies_to_display = handle_test_for_ban(start, end)
    return render(request, "testforban.html", {"movies": movies_to_display})


# Test page that handles data fetch calls and displays movies
def testdisplay(request):
    # Always set these flags as False before committing changes
    delete_all_entries = False      # USE WITH CAUTION, erases movie database contents
    initialize_database = False     # Performs Popular fetch from TMDB 
    get_now_playing_movies = False  # Performs Now Playing fetch from TMDB

    movies_to_display = handle_test_display_page(delete_all_entries, initialize_database, get_now_playing_movies)
    return render(request, "testdisplay.html", {"movies": movies_to_display})