"""
Name of code artifact: banMovie.py
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

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()

# Now you can import your Django models and other modules
from webapp.services import BAN_LIST, load_ban_list
from webapp.models import Movie

def ban_movie(title):
    # Search for the movie title in the actual movie database
    movie = Movie.objects.filter(title__iexact=title).first()

    if movie:
        tmdb_id = movie.tmdb_id

        # Add the TMDB ID to the ban list if not already present
        if str(tmdb_id) not in BAN_LIST:
            with open('webapp/data/ban_movie_list.txt', 'a') as file:
                file.write(f"\n{tmdb_id}")

            # Reload the ban list
            load_ban_list()

            # Remove the movie from the database
            movie.delete()

            print(f"Movie '{title}' (ID: {tmdb_id}) has been banned and removed from the database.")
        else:
            print(f"Movie '{title}' (ID: {tmdb_id}) is already in the ban list.")
    else:
        print(f"Movie '{title}' not found in the database.")

if __name__ == "__main__":
    # Prompt the user for a movie title
    title = input("Enter the movie title you want to ban: ").strip()

    if title:
        ban_movie(title)
    else:
        print("Invalid input. Please enter a valid movie title.")
