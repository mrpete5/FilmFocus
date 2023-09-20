# All requests from external services/website/API here

from webapp.models import *
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
OMDB_API_KEY = os.environ["OMDB_API_KEY"]   # limited to 100,000 calls/day
TMDB_API_KEY = os.environ["TMDB_API_KEY"]
MASTER_LIST = "webapp/data/tmdb_master_movie_list.json"

def load_ban_list():
    with open('webapp/data/ban_movie_list.txt', 'r') as file:
        # Only consider lines that don't start with a '#' comment
        return set(line.strip() for line in file if not line.startswith('#'))
BAN_LIST = load_ban_list()

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
        # Check if the movie is in the ban list
        if str(tmdb_id) in BAN_LIST:
            print(f"Movie '{title}' (ID: {tmdb_id}) is in the ban list and was not added.")
            return
        # Check if the movie exists in the database
        if not Movie.objects.filter(tmdb_id=tmdb_id).exists():
            # Make an API call to fetch more details about the movie from TMDB
            movie_details = fetch_movie_details_from_api(tmdb_id)
            trailer_key = fetch_movie_trailer_key(tmdb_id)  # Fetch the trailer key from TMDB
            
            # Check if the movie is not adult content
            if not movie_details.get('adult'):
                # Extract genres
                genres = movie_details.get('genres', [])
                
                # Extract release year from release_date
                release_date = movie_details.get('release_date')
                release_year = int(release_date.split('-')[0]) if release_date else None
                
                # Create the movie object with TMDB data
                movie = Movie.objects.create(
                    tmdb_id=movie_details.get('id'),
                    title=movie_details.get('title'),
                    overview=movie_details.get('overview'),
                    poster_path=movie_details.get('poster_path'),
                    release_year=release_year,
                    runtime=movie_details.get('runtime'),
                    tagline=movie_details.get('tagline'),
                    trailer_key=trailer_key,
                )
                
                # Fetch additional data from OMDB
                omdb_data = fetch_movie_data_from_omdb(title)
                movie.imdb_rating = omdb_data.get('imdb_rating')
                movie.rotten_tomatoes_rating = omdb_data.get('rotten_tomatoes_rating')
                movie.metacritic_rating = omdb_data.get('metacritic_rating')
                movie.director = omdb_data.get('director')
                movie.box_office = omdb_data.get('box_office')
                movie.save()
                
                # Associate the movie with its genres from TMDB
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



def fetch_movie_data_from_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    movie_data = {}
    for rating in data.get('Ratings', []):
        if rating['Source'] == 'Internet Movie Database':
            movie_data['imdb_rating'] = rating['Value']
        elif rating['Source'] == 'Rotten Tomatoes':
            movie_data['rotten_tomatoes_rating'] = rating['Value']
        elif rating['Source'] == 'Metacritic':
            movie_data['metacritic_rating'] = rating['Value']

    movie_data['director'] = data.get('Director')
    movie_data['box_office'] = data.get('BoxOffice')

    return movie_data




def fetch_movie_trailer_key(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
    headers = {
        "accept": "application/json",
        "Authorization": TMDB_API_KEY,
    }
    response = requests.get(url, headers=headers)
    json_response = response.json()
    results = json_response.get('results', [])

    # Filter the results to get the trailer key
    for result in results:
        if result['type'].lower() == 'trailer':
            return result['key']
    return None


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
