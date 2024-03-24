# Run with "python scripts/update_movie_details.py"
# Update movie details script using TMDb API
# This script fetches and updates movie details from the TMDb API for movies stored in the database.
# 
# Inputs: The script prompts the user to select movies via a console menu:
#   1. Select all movies in the database
#   2. Enter a movie title to fetch and update its details
#
# Outputs: The script prints the progress of fetching and updating movie details for the selected movie entries in the database.
# 
# Authors: Mark, John, Aaron, Traizen, Bill
# Created: 12/18/23
# Last Updated: 03/24/24
#
# Recent Modifications:
# - Added original_language.
# - Added a console menu for selecting movie entries by title or all movies in the database.


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

def update_movie(movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
        if movie.tmdb_id:
            detail = tmdb_movie.details(movie.tmdb_id)
            if detail:
                # Original Language
                if hasattr(detail, 'original_language'):
                    movie.original_language = detail.original_language
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
                # TMDb Popularity
                if hasattr(detail, 'popularity'):
                    movie.tmdb_popularity = detail.popularity
                # Director
                if hasattr(detail, 'credits') and 'crew' in detail.credits:
                    directors = [member['name'] for member in detail.credits['crew'] if member['job'] == 'Director']
                    if directors:
                        movie.director = ', '.join(directors)

                movie.save()
                return True
    except Exception as e:
        print(f"Error updating movie {movie_id}: {e}")
        return False


def print_progress_bar(completed, total):
    percentage = (completed / total) * 100
    bar_length = 50  # Modify this to change the progress bar length
    filled_length = int(round(bar_length * completed / float(total)))
    bar = '=' * filled_length + '>' + ' ' * (bar_length - filled_length)
    print(f"\rProgress: [{bar}] {percentage:.1f}%", end='')


def select_movies():
    selection = input("Select movies to update:\n1. All movies in database \n2. Enter a movie title\nYour choice: ")
    if selection == "1":
        return Movie.objects.all()
    elif selection == "2":
        movie_title = input("Enter the movie title: ")
        return Movie.objects.filter(title__icontains=movie_title)
    else:
        print("Invalid choice. Please select either '1' or '2'.")
        return None


if __name__ == "__main__":
    movies = select_movies()
    if movies:
        movie_ids = list(movies.values_list('id', flat=True))
        total_movies = len(movie_ids)
        completed = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(update_movie, movie_id) for movie_id in movie_ids]
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                print_progress_bar(completed, total_movies)
