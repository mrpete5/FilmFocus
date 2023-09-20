# banMovie.py
import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()

# Now you can import your Django models and other modules
from webapp.services import title_to_id_dict, BAN_LIST, load_ban_list
from webapp.models import Movie


def ban_movie(title):
    # Search for the movie title in the master list
    tmdb_id = title_to_id_dict.get(title.lower())

    if tmdb_id:
        # Add the TMDB ID to the ban list if not already present
        if str(tmdb_id) not in BAN_LIST:
            with open('webapp/data/ban_movie_list.txt', 'a') as file:
                file.write(f"\n{tmdb_id}")

            # Reload the ban list
            load_ban_list()

            # Remove the movie from the database
            Movie.objects.filter(tmdb_id=tmdb_id).delete()

            print(f"Movie '{title}' (ID: {tmdb_id}) has been banned and removed from the database.")
        else:
            print(f"Movie '{title}' (ID: {tmdb_id}) is already in the ban list.")
    else:
        print(f"Movie '{title}' not found in the master list.")

if __name__ == "__main__":
    # Prompt the user for a movie title
    title = input("Enter the movie title you want to ban: ").strip()

    if title:
        ban_movie(title)
    else:
        print("Invalid input. Please enter a valid movie title.")
