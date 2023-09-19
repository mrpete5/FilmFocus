from django.shortcuts import render, HttpResponse
from .models import Movie
from .services import *


# Create your views here.
def index(request):
    return render(request, "index.html")

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
        initialize_movie_database(page_count=2)     # 20 movies per page
    
    items = Movie.objects.all()
    return render(request, "movies.html", {"movies": items})