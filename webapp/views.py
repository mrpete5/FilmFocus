from django.shortcuts import render, HttpResponse
from .models import Movie
from .services import *
import random

def index(request):
    # Fetch the 20 newest releases
    newest_releases = Movie.objects.all().order_by('-release_year')[:20]
    
    # Fetch 8 random movies from the 20 newest releases for "New Movies"
    new_movies = random.sample(list(newest_releases), 8)
    
    # Fetch 6 random movies for "Popular Movies", excluding the ones already selected
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
    delete_all_entries = False   # USE WITH CAUTION, always make False before committing changes
    if delete_all_entries == True:
        clear_movie_database()  # deletes all entries in the movie database, USE WITH CAUTION
    
    database_initialized = True    # always make True before committing changes
    if database_initialized == False:
        initialize_movie_database(page_count=10)     # 20 movies per page
    
    items = Movie.objects.all().order_by('?')[:20]  # Fetch only the first 20 movies
    return render(request, "movies.html", {"movies": items})

