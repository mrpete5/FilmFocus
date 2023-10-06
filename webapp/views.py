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
from .forms import NewUserForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .services import *

# View function for the index page
def index(request):
    context = get_movies_for_index()
    user = request.user
    if user.is_authenticated:
        context['watchlists'] = Watchlist.objects.filter(user=user)
        
    return render(request, 'index.html', context)

# View function for the movie details page
def movie_detail(request, movie_slug):
    movie = get_object_or_404(Movie, slug=movie_slug)
    
    # Fetch recommended movies
    # TODO: Implement this function to fetch Similar & Recommended from
    recommended_movies = movie.get_recommended_movies(10)
    
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
    
    context = {
        'movie': movie,
        'recommended_movies': recommended_movies
    }
    
    return render(request, 'details.html', context)


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
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Hello {username}, welcome back!")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
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
        messages.error(request, "Registration failed")
        messages.error(request, "Fill out all fields")
        messages.error(request, "Please try again")

    else:
        form = NewUserForm()
    return render(request=request, template_name="signup.html", context={"register_form":form})


# View function for the FAQ page
def faq(request):
    return render(request, "faq.html")


# Test page that displays posters for potential movie banning
def testforban(request):
    start_date = "2023-01-01"  # Adjusted start date
    end_date = "2023-10-31"    # Adjusted end date

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



def poster_game(request):
    ''' Play a poster reveal guessing game. '''
    # TODO: Implement this function to play a poster reveal guessing game.    
  
    movies_to_display = handle_poster_game(movie_count=1)
    return render(request, "postergame.html", {"movies": movies_to_display})