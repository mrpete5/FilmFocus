from django.shortcuts import render, HttpResponse
from .models import Movie
from .services import *
import random


def index(request):
    # Fetch movies that are marked as now_playing
    now_playing_movies = Movie.objects.filter(now_playing=True)
    
    # Fetch 12 random movies from the now_playing movies for "New Movies"
    new_movies = random.sample(list(now_playing_movies), min(12, len(now_playing_movies)))
    
    # Fetch 6 random movies for "Popular Movies", excluding the ones already selected as new_movies
    popular_movies = Movie.objects.all().exclude(id__in=[movie.id for movie in new_movies]).order_by('?')[:6]
    
    # Fetch 12 random movies for "More Movies", excluding the ones already selected in new_movies and popular_movies
    more_movies = Movie.objects.all().exclude(id__in=[movie.id for movie in new_movies] + [movie.id for movie in popular_movies]).order_by('?')[:12]
    
    context = {
        'new_movies': new_movies,
        'popular_movies': popular_movies,
        'more_movies': more_movies,
    }
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

def movies(request):
    delete_all_entries = False          # always make False before committing changes, USE WITH CAUTION
    initialize_database = False         # always make False before committing changes
    get_now_playing_movies = False      # always make False before committing changes

    if delete_all_entries == True:
        clear_movie_database()  # deletes all entries in the movie database, USE WITH CAUTION

    if initialize_database == True:
        initialize_movie_database(page_count=1)     # 20 movies per page
    
    if get_now_playing_movies == True:
        fetch_now_playing_movies()
    
    items = Movie.objects.all().order_by('?')[:10]  # Fetch only 10 movies to display
    return render(request, "movies.html", {"movies": items})

