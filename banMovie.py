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
