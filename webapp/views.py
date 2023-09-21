# The functions and html pages render based on the url provided (urls.py)
# More function processing in services.py

from django.shortcuts import render
from .services import *


def index(request):
    context = get_movies_for_index()
    return render(request, 'index.html', context)

def details(request):
    return render(request, "details.html")

def catalog(request):
    return render(request, "catalog.html")

def about(request):
    return render(request, "about.html")

def four04(request):
    return render(request, "404.html")

def signin(request):
    return render(request, "signin.html")

def signup(request):
    return render(request, "signup.html")

def faq(request):
    return render(request, "faq.html")

# Test page that handles data fetch calls
def movies(request):
    # Always set these flags as False before committing changes
    delete_all_entries = False      # USE WITH CAUTION, erases movie database contents
    initialize_database = False     # Performs Popular fetch from TMDB 
    get_now_playing_movies = False  # Performs Now Playing fetch from TMDB

    movies_to_display = handle_movies_page(delete_all_entries, initialize_database, get_now_playing_movies)
    return render(request, "movies.html", {"movies": movies_to_display})
