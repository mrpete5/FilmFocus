"""
Name of code artifact: ban_movie.py
Brief description: Script to ban a movie by its title, preventing it from being displayed in the FilmFocus web application.
Programmer’s name: Mark
Date the code was created: 09/20/2023
Dates the code was revised: None.
Brief description of each revision & author: Initial creation of script to ban movies by title (Mark)
Preconditions: Django environment must be set up correctly. The Django ORM must be available and correctly configured.
Acceptable and unacceptable input values or types: The script expects a valid movie title as input.
Postconditions: The movie is added to the ban list and removed from the database if it exists.
Return values or types: None. The script provides output messages to the console.
Error and exception condition values or types that can occur: Errors can occur if there are issues with database operations or if the movie title is not found.
Side effects: The script modifies the ban list and can remove movies from the database.
Invariants: None.
Any known faults: None.
"""

import os
import django
import sys
import json

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()

# Now you can import your Django models and other modules
from webapp.services import BAN_LIST, load_ban_list
from webapp.models import Movie

JW_WEB_SCRAPER_URLS_PATH = 'webapp/data/jw_web_scraper_urls.json'

def ban_movie(title):
    # Search for the movie title in the actual movie database
    matching_movies = Movie.objects.filter(title__iexact=title)

    if matching_movies.count() > 1:
        print(f"Found {matching_movies.count()} movies with the title '{title}':")
        for i, movie in enumerate(matching_movies, 1):
            print(f"{i}. {movie.title} - {movie.tmdb_popularity}: {movie.overview[:200]}")
        print(f"{matching_movies.count() + 1}. None")

        while True:
            try:
                choice = int(input("Enter the number of the movie you want to ban, or choose 'None': "))
                if 1 <= choice <= matching_movies.count():
                    movie_to_ban = matching_movies[choice - 1]
                    ban_movie_by_id(movie_to_ban)
                    break
                elif choice == matching_movies.count() + 1:
                    print("No movie will be banned.")
                    break
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    elif matching_movies.exists():
        movie_to_ban = matching_movies.first()
        ban_movie_by_id(movie_to_ban)
    else:
        print(f"Movie '{title}' not found in the database.")

def ban_movie_by_id(movie):
    tmdb_id = movie.tmdb_id

    # Add the TMDB ID to the ban list if not already present
    if str(tmdb_id) not in BAN_LIST:
        with open('webapp/data/ban_movie_list.txt', 'a') as file:
            file.write(f"\n{tmdb_id}")

        # Reload the ban list
        load_ban_list()

        # Remove the movie from the database
        movie.delete()

        print(f"Movie '{movie.title}' (ID: {tmdb_id}) has been banned and removed from the database.")
        
        # Remove the movie from the JW web scraper URLs if it exists
        remove_banned_movie_from_jw_urls(tmdb_id)
    else:
        print(f"Movie '{movie.title}' (ID: {tmdb_id}) is already in the ban list.")

def ban_movies_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:  # Set encoding to utf-8
        for line in file:
            title = line.strip()
            if title:
                ban_movie(title)

def remove_banned_movie_from_jw_urls(tmdb_id):
    # Load JW web scraper URLs data
    with open(JW_WEB_SCRAPER_URLS_PATH, 'r') as jw_urls_file:
        jw_urls_data = json.load(jw_urls_file)

    # Remove the movie with the banned TMDB ID
    filtered_jw_urls_data = [movie for movie in jw_urls_data if movie['tmdb_id'] != tmdb_id]

    # Write filtered data back to the JW web scraper URLs file
    with open(JW_WEB_SCRAPER_URLS_PATH, 'w') as jw_urls_file:
        json.dump(filtered_jw_urls_data, jw_urls_file, indent=4)

if __name__ == "__main__":
    # Check if a file is provided as an argument
    if len(sys.argv) > 1 and sys.argv[1].endswith('.txt'):
        file_path = sys.argv[1]
        ban_movies_from_file(file_path)
    else:
        # Existing functionality for single title input
        title = input(" > Enter the movie title you want to ban: ").strip()

        if title:
            ban_movie(title)
        else:
            print("Invalid input. Please enter a valid movie title.")
