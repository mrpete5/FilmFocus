from django.shortcuts import render, HttpResponse
from .models import Movie
from .services import *


# Create your views here.
def index(request):
    return render(request, "index.html")

def index2(request):
    return render(request, "index2.html")

def details1(request):
    return render(request, "details1.html")

def details2(request):
    return render(request, "details2.html")

def catalog1(request):
    return render(request, "catalog1.html")

def catalog2(request):
    return render(request, "catalog2.html")

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
    delete_all_entries = False # USE WITH CAUTION
    if delete_all_entries == True:
        clear_movie_database() # deletes all entries in the movie database, USE WITH CAUTION
    
    database_initialized = True
    if database_initialized == False:
        initialize_movie_database(page_count=10) # 20 movies per page
    
    items = Movie.objects.all()
    return render(request, "movies.html", {"movies": items})