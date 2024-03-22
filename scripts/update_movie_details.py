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
from dotenv import load_dotenv

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

# Now you can import the remaining modules
from tmdbv3api import TMDb, Movie as TMDbMovie
from datetime import datetime
from webapp.models import Movie, Genre
import concurrent.futures

# Your API keys (ensure these are set in your .env file)
OMDB_API_KEY = os.environ.get("OMDB_API_KEY")       # limited to 100,000 calls/day
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")       # limited to around 50 calls/second

# Initialize TMDb
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
tmdb_movie = TMDbMovie()


get_all_movies = False  # Set to True to fetch all movies
movie_title = "Shutter Island"


def update_movie(movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
        if movie.tmdb_id:
            detail = tmdb_movie.details(movie.tmdb_id)
            if detail:
                # Release Date
                if hasattr(detail, 'release_date') and detail.release_date:
                    movie.release_date = datetime.strptime(detail.release_date, '%Y-%m-%d').date()
                # Overview
                if hasattr(detail, 'overview'):
                    movie.overview = detail.overview
                # Poster Path
                if hasattr(detail, 'poster_path'):
                    movie.poster_path = detail.poster_path
                # Release Year
                if hasattr(detail, 'release_date') and detail.release_date:
                    movie.release_year = datetime.strptime(detail.release_date, '%Y-%m-%d').date().year
                # Runtime
                if hasattr(detail, 'runtime'):
                    movie.runtime = detail.runtime
                # Tagline
                if hasattr(detail, 'tagline'):
                    movie.tagline = detail.tagline
                # Genres
                if hasattr(detail, 'genres'):
                    genres = [genre['name'] for genre in detail.genres]
                    movie.genres.clear()  # Clear existing genres
                    for genre_name in genres:
                        genre, _ = Genre.objects.get_or_create(name=genre_name)
                        movie.genres.add(genre)
                # # Trailer Key
                # if hasattr(detail, 'videos') and 'results' in detail.videos:
                #     trailers = [video for video in detail.videos['results'] if video['type'] == 'Trailer']
                #     if trailers:
                #         movie.trailer_key = trailers[0]['key']
                # TMDb Popularity
                if hasattr(detail, 'popularity'):
                    movie.tmdb_popularity = detail.popularity
                # Director
                if hasattr(detail, 'credits') and 'crew' in detail.credits:
                    directors = [member['name'] for member in detail.credits['crew'] if member['job'] == 'Director']
                    if directors:
                        movie.director = ', '.join(directors)
                # # Actors
                # if hasattr(detail, 'credits') and 'cast' in detail.credits:
                #     actors = [member['name'] for member in detail.credits['cast'][:5]]  # Get top 5 actors
                #     if actors:
                #         movie.actors = ', '.join(actors)
                # # Domestic Box Office
                # if hasattr(detail, 'domestic_box_office'):
                #     movie.domestic_box_office = detail.domestic_box_office
                # # MPA Rating
                # if hasattr(detail, 'mpa_rating'):
                #     movie.mpa_rating = detail.mpa_rating

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
    print(f"\rProgress: [{bar}] {percentage:.1f}%", end='')
    
if get_all_movies:
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(update_movie, movie_id) for movie_id in movie_ids]
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            print_progress_bar(completed, total_movies)
else:
    movies = Movie.objects.filter(title=movie_title)
    for movie in movies:
        update_movie(movie.id)