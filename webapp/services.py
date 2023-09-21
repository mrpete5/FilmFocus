# All business logic here, initiated from functions in views.py

from webapp.models import *
import requests
import json
import time
from dotenv import load_dotenv
import os
import random


load_dotenv()
OMDB_API_KEY = os.environ["OMDB_API_KEY"]               # limited to 100,000 calls/day
TMDB_API_KEY_STRING = os.environ["TMDB_API_KEY_STRING"] # limited to around 50 calls/second
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

def search_movie_by_title(title):
    return title_to_id_dict.get(title.lower())


def search_movie_by_id(tmdb_id):
    return id_to_title_dict.get(tmdb_id)


def search_and_fetch_movie_by_title(title):
    tmdb_id = search_movie_by_title(title)
    process_movie_search(tmdb_id, title)


def search_and_fetch_movie_by_id(tmdb_id):
    title = search_movie_by_id(tmdb_id)
    process_movie_search(tmdb_id, title)


def process_movie_search(tmdb_id, title, now_playing=False):
    # Check if the movie is in the TMDB master list
    if not tmdb_id:
        print(f"Movie '{title}' not found in the master list.")
        return
    
    # Check if the movie is in the ban list
    if str(tmdb_id) in BAN_LIST:
        print(f"Movie '{title}' (ID: {tmdb_id}) is in the ban list and was not added.")
        return

    # Make an API call to fetch more details about the movie from TMDB
    movie_details = fetch_movie_details_from_tmdb(tmdb_id)
    
    # Check if the movie is adult content
    if movie_details.get('adult'):
        print(f"Movie '{title}' (ID: {tmdb_id}) is for adults and was not added.")
        return
            
    # Check if the movie exists in the database
    if Movie.objects.filter(tmdb_id=tmdb_id).exists():
        # If the movie already exists, update its now_playing status
        Movie.objects.filter(tmdb_id=tmdb_id).update(now_playing=now_playing)
        print(f"Movie '{title}' (ID: {tmdb_id}) already exists in the database.")
        return

    # Fetch the trailer key from TMDB
    trailer_key = fetch_movie_trailer_key(tmdb_id)
    # Extract release year from release_date
    release_date = movie_details.get('release_date')
    release_year = int(release_date.split('-')[0]) if release_date else None
    
    # Verify now_playing is either 2023 or 2024
    if now_playing and release_year not in [2023, 2024]:
        now_playing = False
    
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
        now_playing=now_playing,
    )
    
    # Fetch additional data from OMDB
    omdb_data = fetch_movie_data_from_omdb(title)
    movie.imdb_rating = omdb_data.get('imdb_rating')
    movie.rotten_tomatoes_rating = omdb_data.get('rotten_tomatoes_rating')
    movie.metacritic_rating = omdb_data.get('metacritic_rating')
    movie.director = omdb_data.get('director')
    movie.domestic_box_office = omdb_data.get('domestic_box_office')
    movie.mpa_rating = omdb_data.get('mpa_rating')
    movie.save()

    # Extract genres
    genres = movie_details.get('genres', [])        
    # Associate the movie with its genres from TMDB
    for genre_data in genres:
        genre, created = Genre.objects.get_or_create(name=genre_data['name'])
        movie.genres.add(genre)
    
    print(f"Movie '{title}' (ID: {tmdb_id}) fetched and saved to the database.")


def fetch_movie_details_from_tmdb(tmdb_id):
    # Define the TMDB API endpoint and parameters
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US"
    headers = {
        "accept": "application/json",
        'Authorization': TMDB_API_KEY_STRING,
    }
    # Fetch movie details from TMDB
    response = requests.get(url, headers=headers)
    return response.json()


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
    movie_data['domestic_box_office'] = data.get('BoxOffice')
    movie_data['mpa_rating'] = data.get('Rated')
    return movie_data


def fetch_movie_trailer_key(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
    headers = {
        "accept": "application/json",
        "Authorization": TMDB_API_KEY_STRING,
    }
    response = requests.get(url, headers=headers)
    json_response = response.json()
    results = json_response.get('results', [])

    # Filter the results to get the trailer key
    for result in results:
        if result['type'].lower() == 'trailer':
            return result['key']
    return None


def fetch_popular_movies(start_page=1, end_page=5):
    # Set now_playing to False for all movies
    Movie.objects.update(is_popular=False)
    
    for page_num in range(start_page, end_page + 1):
        print(f"Fetching popular movies page number {page_num}")
        url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page_num}"
        headers = {
            "accept": "application/json",
            "Authorization": TMDB_API_KEY_STRING,
        }
        response = requests.get(url, headers=headers)
        json_response = response.json()
        results = json_response['results']

        for movie in results:
            movie_id = movie["id"]
            search_and_fetch_movie_by_id(movie_id)
            
            if page_num <= 5:
                # Set is_popular to True for the movie
                Movie.objects.filter(tmdb_id=movie_id).update(is_popular=True)
        
        if page_num != end_page:  # No need to sleep after fetching the last page
            time.sleep(1)
    return json_response


def fetch_now_playing_movies():
    # Set now_playing to False for all movies
    Movie.objects.update(now_playing=False)

    for page_num in range(1, 6):  # Fetch the first 5 pages
        print(f"Fetching now playing movies page number {page_num}")
        url = f"https://api.themoviedb.org/3/movie/now_playing?language=en-US&page={page_num}"
        headers = {
            "accept": "application/json",
            "Authorization": TMDB_API_KEY_STRING,
        }
        response = requests.get(url, headers=headers)
        movies = response.json().get('results', [])

        for movie in movies:
            tmdb_id = movie.get('id')
            title = movie.get('title')
            # Process each movie using the process_movie_search function
            process_movie_search(tmdb_id, title, now_playing=True)


def get_movies_for_index():
    # Fetch movies that are marked as now_playing
    now_playing_movies = Movie.objects.filter(now_playing=True)
    # Fetch 12 random movies from the now_playing movies for "New Movies"
    new_movies = random.sample(list(now_playing_movies), min(12, len(now_playing_movies)))
    
    # Fetch all movies that are marked as popular
    all_popular_movies = Movie.objects.filter(is_popular=True).exclude(id__in=[movie.id for movie in new_movies])
    # Randomly select 6 movies from those marked as popular
    popular_movies = random.sample(list(all_popular_movies), min(6, len(all_popular_movies)))
    
    # Fetch the top 60 movies based on imdb_rating
    top_60_movies = Movie.objects.all().exclude(id__in=[movie.id for movie in new_movies] + [movie.id for movie in popular_movies]).order_by('-imdb_rating')[:60]
    # Randomly select 6 movies from the top 60
    top_rated_movies = random.sample(list(top_60_movies), min(6, len(top_60_movies)))
    
    # Fetch 12 random movies for "More Movies", excluding the ones already selected in new_movies, popular_movies, and top_rated_movies
    more_movies = Movie.objects.all().exclude(id__in=[movie.id for movie in new_movies] + [movie.id for movie in popular_movies] + [movie.id for movie in top_rated_movies]).order_by('?')[:12]
    
    return {
        'new_movies': new_movies,
        'popular_movies': popular_movies,
        'top_rated_movies': top_rated_movies,
        'more_movies': more_movies,
    }


def clear_movie_database():
    deleted_count, _ = Movie.objects.all().delete()
    print(f"{deleted_count} movies deleted from the database.")


def handle_movies_page(delete_all_entries=False, initialize_database=False, get_now_playing_movies=False):
    page_count = 5
    
    if delete_all_entries:
        clear_movie_database()  # deletes all entries in the movie database, USE WITH CAUTION

    if initialize_database:
        fetch_popular_movies(1, end_page=page_count)  # 20 movies per page
        fetch_now_playing_movies()  # Fetch now playing movies after initializing the database
    elif get_now_playing_movies:  # Use 'elif' to ensure it doesn't run again if initialize_database is True
        fetch_now_playing_movies()
    
    items = Movie.objects.all().order_by('?')[:10]  # Fetch only 10 movies to display
    return items
