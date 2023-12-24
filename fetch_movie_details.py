# This is a script that will get all of the movie details for a movie entry in our model Movie.
# Inputs: User provides the movie title and release year.
# Outputs: Script prints all of the movie details for the selected movie entry that we have saved in our database.
# Author: Mark
# Created: 12/17/23
# Last Updated: 12/18/23
# Recent Modifications: Added this prologue comment block.

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()

from webapp.models import Movie

def get_movie_details(title, release_year):
    movie = Movie.objects.filter(title=title, release_year=release_year).first()

    if movie:
        print(f"\nTitle: {movie.title}")
        print(f"Release Year: {movie.release_year}")
        print(f"TMDb ID: {movie.tmdb_id}")
        print(f"IMDb ID: {movie.imdb_id}")
        print(f"Overview: {movie.overview}")
        print(f"Poster Path: {movie.poster_path}")
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

        print("Genres:")
        for genre in movie.genres.all():
            print(f"- {genre.name}")

        print("Streaming Providers:")
        for provider in movie.streaming_providers.all():
            print(f"- {provider.name}")

    else:
        print(f"Movie '{title}' released in {release_year} not found.")

    print("\n")


def main():
    while True:
        movie_title = input("Enter movie title (or 'exit' to quit): ").strip()
        if movie_title.lower() == 'exit':
            break

        try:
            release_year = int(input("Enter release year: ").strip())
        except ValueError:
            print("Invalid input for release year. Please enter a valid year.")
            continue

        get_movie_details(movie_title, release_year)

if __name__ == "__main__":
    main()
