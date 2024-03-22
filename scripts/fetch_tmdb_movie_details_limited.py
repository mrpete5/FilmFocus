import os
import sys
import django
import concurrent.futures
from dotenv import load_dotenv
from tmdbv3api import TMDb, Movie as TMDbMovie
from datetime import datetime, date
import json
import random  # Import the random module

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

get_random = True   # Set to True to fetch random movies
limit_count = 3     # Change the limit_count as needed

# Define the function to recursively convert object to dictionary
def obj_to_dict(obj):
    if hasattr(obj, '__dict__'):
        return {key: obj_to_dict(value) for key, value in obj.__dict__.items() if not callable(value) and not key.startswith('_')}
    elif isinstance(obj, (list, tuple)):
        return [obj_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: obj_to_dict(value) for key, value in obj.items()}
    else:
        return obj

# Define the function to fetch and save movie details
def fetch_and_save_movie_details(movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
        if movie.tmdb_id:
            # print(f"Fetching details for {movie_id}: {movie.title} ({movie.release_year})...")
            detail = tmdb_movie.details(movie.tmdb_id)
            if detail:
                # Convert detail object to dictionary
                detail_dict = obj_to_dict(detail)
                print(f"Successful fetch for {movie_id}: {movie.title} ({movie.release_year})")
                # Create a file name based on the movie ID
                filename = f"movie_{movie_id}_details.json"
                # Write the movie details to a JSON file
                with open(filename, 'w') as file:
                    json.dump(detail_dict, file, indent=4)
                return True
    except Exception as e:
        print(f"Error fetching details for movie {movie_id}: {e}")
        return False

# Get a random selection of movie IDs if get_random is True
if get_random:
    movie_ids = list(Movie.objects.values_list('id', flat=True))
    random.shuffle(movie_ids)
    movie_ids = movie_ids[:limit_count]
else:
    movie_ids = list(Movie.objects.values_list('id', flat=True))[:limit_count]

total_movies = len(movie_ids)
completed = 0

# Function to print a progress bar
def print_progress_bar(completed, total):
    percentage = (completed / total) * 100
    bar_length = 50  # Modify this to change the progress bar length
    filled_length = int(round(bar_length * completed / float(total)))
    bar = '=' * filled_length + '>' + ' ' * (bar_length - filled_length)
    print(f"\rProgress: [{bar}] {percentage:.2f}%", end='')

# Execute fetch_and_save_movie_details concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(fetch_and_save_movie_details, movie_id) for movie_id in movie_ids]
    for future in concurrent.futures.as_completed(futures):
        completed += 1
        # print_progress_bar(completed, total_movies)
