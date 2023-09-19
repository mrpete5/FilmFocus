# All requests from external services/website/API here

from webapp.models import *
import requests
import json
import time

MASTER_LIST = "webapp/data/master_movie_list.json"
TMDB_API_KEY = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhYTE1N2I1NDc5MjI3Yjc2YTg4NDUzMjM4NGU4ZDI4MCIsInN1YiI6IjYzN2I4ZjcxMzM2ZTAxMDA5YmU2MzdlNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Cs25S_3XLZpGbtHRZmRJaKMJ8FwSvmkTolQxG5TnRbE'

# Load the master list from the JSON file into a Python list
with open(MASTER_LIST, 'r', encoding='utf-8') as file:
    master_list = json.load(file)

# Convert the master list into dictionaries for faster lookups
title_to_id_dict = {movie['original_title'].lower(): movie['id'] for movie in master_list}
id_to_title_dict = {movie['id']: movie['original_title'] for movie in master_list}


def fetch_movie_details_from_api(tmdb_id):
    # Define the TMDB API endpoint and parameters
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US"
    headers = {
        "accept": "application/json",
        'Authorization': TMDB_API_KEY,
    }
    # Fetch movie details from TMDB
    response = requests.get(url, headers=headers)
    return response.json()


def search_movie_by_title(title):
    return title_to_id_dict.get(title.lower())


def search_movie_by_id(tmdb_id):
    return id_to_title_dict.get(tmdb_id)

## Example usages
# search_and_fetch_movie_by_title("Forrest Gump")
# search_and_fetch_movie_by_id(18)

def search_and_fetch_movie_by_title(title):
    tmdb_id = search_movie_by_title(title)
    process_movie_search(tmdb_id, title)


def search_and_fetch_movie_by_id(tmdb_id):
    title = search_movie_by_id(tmdb_id)
    process_movie_search(tmdb_id, title)


def process_movie_search(tmdb_id, title):
    if tmdb_id:
        # Check if the movie exists in the database
        if not Movie.objects.filter(tmdb_id=tmdb_id).exists():
            # Make an API call to fetch more details about the movie
            movie_details = fetch_movie_details_from_api(tmdb_id)
            
            # Check if the movie is not for adults
            if not movie_details.get('adult'):
                # Extract genres
                genres = movie_details.get('genres', [])
                
                # Extract release year from release_date
                release_date = movie_details.get('release_date')
                release_year = int(release_date.split('-')[0]) if release_date else None
                
                # Create the movie object
                movie = Movie.objects.create(
                    tmdb_id=movie_details.get('id'),
                    title=movie_details.get('title'),
                    overview=movie_details.get('overview'),
                    poster_path=movie_details.get('poster_path'),
                    release_year=release_year,
                    runtime=movie_details.get('runtime'),
                    tagline=movie_details.get('tagline')
                )
                
                # Associate the movie with its genres
                for genre_data in genres:
                    genre, created = Genre.objects.get_or_create(name=genre_data['name'])
                    movie.genres.add(genre)
                
                print(f"Movie '{title}' (ID: {tmdb_id}) fetched and saved to the database.")
            else:
                print(f"Movie '{title}' (ID: {tmdb_id}) is for adults and was not added.")
        else:
            print(f"Movie '{title}' (ID: {tmdb_id}) already exists in the database.")
    else:
        print(f"Movie '{title}' not found in the master list.")



def fetch_popular_movies(page_num):
    url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page_num}"
    headers = {
        "accept": "application/json",
        "Authorization": TMDB_API_KEY,
    }
    response = requests.get(url, headers=headers)
    json_response = response.json()
    results = json_response['results']

    for movie in results:
        movie_id = movie["id"]
        search_and_fetch_movie_by_id(movie_id)
    return json_response


def fetch_multiple_pages(start_page, end_page):
    for page_num in range(start_page, end_page + 1):
        print(f"Fetching page {page_num}...")
        fetch_popular_movies(page_num)
        if page_num != end_page:  # No need to sleep after fetching the last page
            time.sleep(1)

def initialize_movie_database(page_count):
    fetch_multiple_pages(1, page_count)

def clear_movie_database():
    deleted_count, _ = Movie.objects.all().delete()
    print(f"{deleted_count} movies deleted from the database.")
