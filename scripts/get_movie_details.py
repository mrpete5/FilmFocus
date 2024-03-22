# This script retrieves details of a movie from our Movie model.
# Inputs: User provides the movie title.
# Outputs: The script prints all the details of the selected movie entry stored in our database.
# Author: Mark
# Created: 12/17/23
# Last Updated: 03/21/24
# Recent Modifications: Updated script to remove release year, but handle multiple matching movie titles


import os
import sys
import django

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Append the parent directory (FilmFocus) to the system path
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()
from webapp.models import Movie

def search_movie(title):
    matching_movies = Movie.objects.filter(title__iexact=title)

    if matching_movies.count() > 1:
        print(f"Found {matching_movies.count()} movies with the title '{title}':")
        for i, movie in enumerate(matching_movies, 1):
            print(f"{i}. {movie.title} ({movie.release_year})- {movie.tmdb_popularity}: {movie.overview[:200]}")
        print(f"{matching_movies.count() + 1}. None")

        while True:
            try:
                choice = int(input("Enter the number of the movie you want to view details for, or choose 'None': "))
                if 1 <= choice <= matching_movies.count():
                    return matching_movies[choice - 1]
                elif choice == matching_movies.count() + 1:
                    print("No movie selected.")
                    return None
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    elif matching_movies.count() == 1:
        return matching_movies.first()
    else:
        print(f"No movies found with the title '{title}'.")
        return None

def print_movie_details(movie):
    print(f"\nTitle: {movie.title}")
    print(f"Release Year: {movie.release_year}")
    print(f"TMDb ID: {movie.tmdb_id}")
    print(f"IMDb ID: {movie.imdb_id}")
    print(f"TMDb Popularity: {movie.tmdb_popularity}")
    print(f"Overview: {movie.overview}")
    print(f"Poster Path: https://image.tmdb.org/t/p/w500{movie.poster_path}")
    print(f"Runtime: {movie.runtime}")
    print(f"Tagline: {movie.tagline}")
    print(f"IMDb Rating: {movie.imdb_rating}")
    print(f"Letterboxd Rating: {movie.letterboxd_rating}")
    print(f"Rotten Tomatoes Rating: {movie.rotten_tomatoes_rating}")
    print(f"Metacritic Rating: {movie.metacritic_rating}")
    print(f"Director: {movie.director}")
    print(f"Domestic Box Office: {movie.domestic_box_office}")
    print(f"MPA Rating: {movie.mpa_rating}")
    print(f"Now Playing: {movie.now_playing}")
    print(f"Last Updated: {movie.last_updated}")
    genres_str = ", ".join([genre.name for genre in movie.genres.all()])
    print(f"Genres: {genres_str}")
    streamers_str = ", ".join([streamer.name for streamer in movie.streaming_providers.all()])
    print(f"Streaming Providers: {streamers_str}")
    print()

def main():
    while True:
        movie_title = input("Enter movie title (or 'exit' to quit): ").strip()
        quit_words = ["exit", "quit", "q"]
        if movie_title.lower() in quit_words:
            break

        movie = search_movie(movie_title)
        if movie:
            print_movie_details(movie)

if __name__ == "__main__":
    main()
