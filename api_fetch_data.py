"""
Name of code artifact: api_fetch_data.py
Description: Replaces testdisplay/ page and webapp.services.handle_test_display_page().
        Contains business logic for the FilmFocus web application, including functions to 
        fetch movie details from TMDB and OMDB, and to manage the movie database.
"""

import os
import django
# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()

import datetime
import time
from webapp.models import *
from webapp.services import *


# Handle the test display page and manage the movie database
def api_fetch_data(settings):
    # 20 movies per page
    # update_streaming_providers(test_limit=10) # Uncomment to update the top streaming providers

    # search_and_fetch_movie_by_title("The Greasy Strangler")
    # search_and_fetch_movie_by_id(775517)

    # popular_pages is the main method for getting a mass amount of new movies
    popular_pages = 10          # Number of popular pages from 1 to x with 20 results each, TMDb
    now_playing_pages = 10      # Number of now playing pages from 1 to x with 20 results each, TMDb
    fetch_discover_count = 5    # Number of discover pages from 1 to x with 20 results each, TMDb
    # tmdb_id_value = 11          # Initialized value
    
    flags = [
        'erase_movie_db',                     # settings[0], USE WITH CAUTION
        'init_movie_db',                      # settings[1], Can take a while based on settings/quantities
        'get_now_playing',                    # settings[2], Can take a while based on settings/quantities
        'update_streaming',                   # settings[3], Takes a while, performed on entire movie database
        'update_recs',                        # settings[4], Takes a while, performed on entire movie database
        'get_discover_movies',                # settings[5], Takes a while, performed on entire movie database
        'update_letterboxd',                  # settings[6], performed on entire movie database
        'get_specific_movie_by_search',       # settings[7], Should be very fast but may be unsuccessful
        'update_omdb_movie_ratings',          # settings[8], Takes a while, performed on entire movie database
        'update_all_db_movie_entries',        # settings[9], Takes a while, performs updates on all movies in db (ratings, streaming, recs)
    ]

    descriptions = [
        'Erases all movie database contents',
        'Performs Popular and Now Playing fetch from TMDB',
        'Performs Now Playing fetch from TMDB',
        'Updates all movie streaming providers from TMDB',
        'Updates all movie recommendations from TMDB',
        'Fetches all discover movies from TMDB',
        'Updates all movie letterboxd info from webscraper',
        'Fetches a specific movie by title', 
        'Updates all movie IMDb, RT, and Metacritic ratings, takes a while',
        'Updates all movie entries (letterboxd, streaming, recommendations)',
    ]

    # Print the menu
    print("Select the settings you want to set as True:")
    for i, (flag, description) in enumerate(zip(flags, descriptions)):
        print(f"{i+1}. {flag} - {description}")

    # Ask the user for comma-separated numbers corresponding to the settings they want to set as True
    user_input = input("Enter comma-separated numbers of the settings you want to set as True: ")
    selected_numbers = [int(num) for num in user_input.split(",")]

    # Set selected settings as True
    for num in selected_numbers:
        settings[num-1] = True


    # Diplay the starting time of the test display page
    now_time = time.time()
    now_time_readable = datetime.datetime.fromtimestamp(now_time).strftime('%H:%M:%S')
    print(f'Starting api_fetch_data at {now_time_readable}\n')
        
    if settings[0]:
        # Verification check for clearing database
        verify = input("Are you sure you want to clear the database? (yes/no): ")
        if verify.lower() == 'yes':
            timer(function_name='clear_movie_database', fetch_func=clear_movie_database, args={})
        else:
            settings[0] = False
            print("Database not cleared.")

    if settings[1]:
        timer(function_name='fetch_popular_movies', fetch_func=fetch_popular_movies, args={'start_page': 1, 'end_page': popular_pages})
        timer(function_name='fetch_now_playing_movies', fetch_func=fetch_now_playing_movies, args={'start_page': 1, 'end_page': now_playing_pages })
    elif settings[2]:  # Use 'elif' to ensure it doesn't run again if initialize_database is True
        timer(function_name='fetch_now_playing_movies', fetch_func=fetch_now_playing_movies, args={'start_page': 1, 'end_page': now_playing_pages})
    
    if settings[3]:
        timer(function_name='update_streaming_providers', fetch_func=update_streaming_providers, args={})
    
    if settings[4]:
        timer(function_name='update_movie_recommendations', fetch_func=update_movie_recommendations, args={})
    
    if settings[5]:
        timer(function_name='fetch_tmdb_discover_movies', fetch_func=fetch_tmdb_discover_movies, args={'start_page': 1, 'end_page': fetch_discover_count})

    if settings[6]:
        timer(function_name="update_letterboxd_ratings", fetch_func=update_letterboxd_ratings, args={})
    
    if settings[7]:
        search_term = input("Enter search term: ")
        search_and_fetch_movie_by_title(search_term)        # Search for a movie by its title and fetch its details
        # search_and_fetch_movie_by_id(tmdb_id_value)         # Search for a movie by its tmdb_id and fetch its details
    
    if settings[8]:
        timer(function_name='update_omdb_movie_ratings', fetch_func=update_omdb_movie_ratings, args={})
    
    if settings[9]:
        """ Performs all operations to update movie data in our database, without deleting anything. """
        """ Updates all movie ratings, streaming providers, and recommendations. """
        get_movies = True
        get_updates = True

        if get_movies:
            timer(function_name='fetch_popular_movies', fetch_func=fetch_popular_movies, args={'start_page': 1, 'end_page': popular_pages})
            timer(function_name='fetch_now_playing_movies', fetch_func=fetch_now_playing_movies, args={'start_page': 1, 'end_page': now_playing_pages })
            timer(function_name='fetch_tmdb_discover_movies', fetch_func=fetch_tmdb_discover_movies, args={'start_page': 1, 'end_page': fetch_discover_count})

        if get_updates:
            timer(function_name='update_streaming_providers', fetch_func=update_streaming_providers, args={})
            # timer(function_name='update_movie_recommendations', fetch_func=update_movie_recommendations, args={})     # needs to be threaded
            timer(function_name="update_letterboxd_ratings", fetch_func=update_letterboxd_ratings, args={})
            timer(function_name='update_omdb_movie_ratings', fetch_func=update_omdb_movie_ratings, args={})

    # Prints which settings are set
    print("==========================")
    for flag, setting in zip(flags, settings):
        print(f"{flag} = {setting}")
    print("==========================\n")


# Initialize settings list
settings = [False] * 10

# Call the function with settings
api_fetch_data(settings)