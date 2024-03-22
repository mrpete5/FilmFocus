# Fetch all of the movie release dates using TMDb to update the database.
# Just run "python scripts/fetch_release_date.py"
# This is a script that will get all of the movie release dates for a movie entry in our model Movie.
# Inputs: No inputs
# Outputs: Script prints all of the movie details for the selected movie entry that we have saved in our database.
# Author: Mark
# Created: 12/18/23
# Last Updated: 12/18/23
# Recent Modifications: Initialized script.

import os
import sys
import django
import concurrent.futures
from dotenv import load_dotenv
from tmdbv3api import TMDb, Movie as TMDbMovie
from datetime import datetime

# Load environment variables first
load_dotenv()

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Append the parent directory (FilmFocus) to the system path
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()

# Import the Movie model after setting up Django
from webapp.models import Movie

# Your API keys (ensure these are set in your .env file)
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")               # limited to 100,000 calls/day
# TMDB_API_KEY_STRING = os.environ.get("TMDB_API_KEY_STRING") # limited to around 50 calls/second
TMDB_API_KEY_STRING = "f958ac9e78a958932e6def76077a2292"


# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY_STRING
tmdb_movie = TMDbMovie()

def update_movie(movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
        if movie.tmdb_id:
            detail = tmdb_movie.details(movie.tmdb_id)
            if detail and hasattr(detail, 'release_date') and detail.release_date:
                movie.release_date = datetime.strptime(detail.release_date, '%Y-%m-%d').date()
                movie.save()
                return True
    except Exception as e:
        print(f"Error updating movie {movie_id}: {e}")
        return False

movie_ids = list(Movie.objects.values_list('id', flat=True))
total_movies = len(movie_ids)
completed = 0

def print_progress_bar(completed, total):
    percentage = (completed / total) * 100
    bar_length = 50  # Modify this to change the progress bar length
    filled_length = int(round(bar_length * completed / float(total)))
    bar = '=' * filled_length + '>' + ' ' * (bar_length - filled_length)
    print(f"\rProgress: [{bar}] {percentage:.2f}%", end='')
    

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(update_movie, movie_id) for movie_id in movie_ids]
    for future in concurrent.futures.as_completed(futures):
        completed += 1
        print_progress_bar(completed, total_movies)
