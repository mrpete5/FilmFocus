"""
Name of code artifact: services.py
Brief description: Contains business logic for the FilmFocus web application, including functions to fetch movie details from TMDB and OMDB, and to manage the movie database.
Programmer’s name: Mark, Aaron, Bill, John, Traizen
Date the code was created: 09/18/2023
Date the code was revised: 03/25/2024
Brief description of each revision & author: Added threading to multiple API calling functions
Preconditions: Django environment must be set up correctly, and necessary environment variables (API keys) must be available.
Acceptable and unacceptable input values or types: Functions expect specific types as documented in their respective comments.
Postconditions: Functions return values or modify the database as per their documentation.
Return values or types: Varies based on the function.
Error and exception condition values or types that can occur: Errors can occur if API limits are reached or if there are issues with the database.
Side effects: Some functions modify the database.
Invariants: None.
Any known faults: None.
"""

import threading
import time
import datetime
import os
import random
import requests
import json
import webapp.letterboxd_scraper as lbd_scrape
import webapp.just_watch_scraper as jw_scrape
import concurrent.futures
from webapp.models import *
from dotenv import load_dotenv
from django.db.models import F, Max, Avg
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore


# Load environment variables
load_dotenv()
OMDB_API_KEY = os.environ["OMDB_API_KEY"]               # limited to 100,000 calls/day
TMDB_API_KEY_STRING = os.environ["TMDB_API_KEY_STRING"] # limited to around 50 calls/second
MASTER_LIST = "webapp/data/tmdb_master_movie_list.json"
ALLOWED_PROVIDERS_LIST = "webapp/data/allowed_providers_list.txt"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "accept": "application/json",
    'Authorization': TMDB_API_KEY_STRING,
}

# Load the ban list from the file
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

# Read allowed providers and store them in the filtered_providers list
filtered_providers = []
with open(ALLOWED_PROVIDERS_LIST, 'r') as input_file:
    for line in input_file:
        provider_name = line.strip()
        filtered_providers.append(provider_name)

# Create a lock for database access
database_lock = threading.Lock()

# Search for movies by their title
def search_movie_by_title(title):
    lower_title = title.lower()
    return [movie['id'] for movie in master_list if movie['original_title'].lower() == lower_title]

# Search for a movie by its TMDB ID
def search_movie_by_id(tmdb_id):
    return id_to_title_dict.get(tmdb_id)

# Search for movies by their title and fetch their details
def search_and_fetch_movie_by_title(title):
    tmdb_ids = search_movie_by_title(title)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
        futures = [executor.submit(process_movie_search, tmdb_id, search_movie_by_id(tmdb_id)) for tmdb_id in tmdb_ids]
        for future in concurrent.futures.as_completed(futures):
            # Handle any results or exceptions here if needed
            pass

# Search for a movie by its TMDB ID and fetch its details
def search_and_fetch_movie_by_id(tmdb_id):
    title = search_movie_by_id(tmdb_id)
    process_movie_search(tmdb_id, title)

# Convert a number of seconds to a readable time string
def seconds_to_readable_time(estimate_time_secs):
    estimate_time_secs = int(estimate_time_secs)
    minutes, seconds = divmod(estimate_time_secs, 60)
    hours, minutes = divmod(minutes, 60)
    hours_label = "hour" if hours == 1 else "hours"
    minutes_label = "minute" if minutes == 1 else "minutes"
    seconds_label = "second" if seconds == 1 else "seconds"
    time_components = []
    if hours > 0:
        time_components.append(f"{hours} {hours_label}")
    if minutes > 0:
        time_components.append(f"{minutes} {minutes_label}")
    if seconds > 0:
        time_components.append(f"{seconds} {seconds_label}")
    return ', '.join(time_components)


# Determines the Rotten Tomatoes icon based on the Rotten Tomatoes rating
def determine_rt_icon(rt_rating):
    if rt_rating is not None:
        if rt_rating >= 75:
            return 'img/logos/Rotten_Tomatoes_certified_fresh.png'
        elif rt_rating >= 60:
            return 'img/logos/Rotten_Tomatoes_fresh.png'
        else:
            return 'img/logos/Rotten_Tomatoes_rotten.png'
    return None

# Retrieve the watchlists for a user
def get_watchlists_for_user(user):
    watchlists = Watchlist.objects.filter(user=user)
    return watchlists

# Progress bar for a given function
def progress_bar(title, current, total, bar_length=100):
    title = f'  {title}'
    percent = float(current) * 100 / total
    arrow_count = int(percent/100 * bar_length - 1)
    arrow_str = "=" * arrow_count + '>'
    spaces = ' ' * (bar_length - len(arrow_str))
    end_char = '\r' if current < total else '\n'
    print(f'\r{title}: [{arrow_str}{spaces}] {percent:.0f}%  ', end=end_char)

# Progress bar handler, if wait is iteration-based    
def progress_bar_iteration(title, current, num_iterations):
    progress_bar(title, current, num_iterations, bar_length=80)
    
# Progress bar handler, if wait is time-based    
def progress_bar_time(title, wait_seconds):
    for count in range(wait_seconds + 1):
        progress_bar(title, count, wait_seconds, bar_length=80)
        time.sleep(1)

# Timer for testing funtions
def timer(function_name, fetch_func, args):
    ''' Timer function to print out the time elapsed for each function call. '''

    start_time = time.time()
    start_time_readable = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
    print(f'Start {function_name}: {start_time_readable}')

    movies = fetch_func(**args) # Call the function here, don't do anything with the output

    end_time = time.time()
    end_time_readable = datetime.datetime.fromtimestamp(end_time).strftime('%H:%M:%S')  

    total_time_secs = end_time - start_time

    # Convert seconds to HH:MM:SS
    hours, remainder = divmod(total_time_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_time_readable = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

    print(f'Finished {function_name}: {end_time_readable}')
    print(f'Total time for {function_name}: {total_time_readable}.\n')


# Process the search results for a movie and fetch its details
def process_movie_search(tmdb_id, title, now_playing=False, allowed_providers=filtered_providers):
    ''' Process the search results for a movie and fetch its details. '''
    
    # Check if the movie is in the TMDB master list
    if not tmdb_id:
        print(f"Movie '{title}' not found in the master list.")
        return
    
    # Check if the movie is in the ban list
    if str(tmdb_id) in BAN_LIST:
        print(f"Ban List: {title} (ID: {tmdb_id}) was not retrieved")
        return

    # Check if the movie exists in the database
    if Movie.objects.filter(tmdb_id=tmdb_id).exists():
        existing_movie = Movie.objects.get(tmdb_id=tmdb_id)
        existing_release_year = existing_movie.release_year
        
        # Verify now_playing is either 2023 or 2024
        if now_playing and existing_release_year not in [2023, 2024]:
            now_playing = False

        # Update its now_playing status
        Movie.objects.filter(tmdb_id=tmdb_id).update(now_playing=now_playing)
        return

    # Make an API call to fetch more details about the movie from TMDB
    movie_details = fetch_movie_details_from_tmdb(tmdb_id)
    
    # Check if the movie is adult content
    if movie_details.get('adult'):
        return
    
    overview = movie_details.get('overview')
    poster_path=movie_details.get('poster_path')
    # Check if the movie has an overview and a poster
    if not overview or not poster_path:
        return

    # Extract release year from release_date
    release_date = movie_details.get('release_date')
    release_year = int(release_date.split('-')[0]) if release_date else None
    
    # Verify now_playing is either 2023 or 2024
    if now_playing and release_year not in [2023, 2024]:
        now_playing = False

    # Extract the video results and fetch the trailer key
    videos = movie_details.get('videos', {}).get('results', [])
    trailer_key = fetch_movie_trailer_key(videos)
    
    imdb_id = movie_details.get('imdb_id')
    # Create the movie object with TMDB data
    movie = Movie.objects.create(
        tmdb_id=movie_details.get('id'),
        imdb_id=imdb_id,
        tmdb_popularity=movie_details.get('popularity'),
        title=movie_details.get('title'),
        overview=overview,
        poster_path=poster_path,
        release_date=release_date,
        release_year=release_year,
        runtime=movie_details.get('runtime'),
        tagline=movie_details.get('tagline'),
        trailer_key=trailer_key,
        now_playing=now_playing,
        original_language = movie_details.get('original_language'),
    )
    movie.save()
    
    # Extract recommendations
    recommendations = movie_details.get('recommendations', {}).get('results', [])
    recommended_movie_data = []
    for rec in recommendations:
        rec_popularity = rec.get('popularity', 0)  # Default to 0 if popularity is not present
        if rec_popularity > 10:
            recommended_movie_data.append({
                'tmdb_id': rec.get('id'),
                'title': rec.get('title'),
                'tmdb_popularity': rec_popularity  # Store the tmdb_popularity here
            })

    movie.recommended_movie_data = recommended_movie_data

    # Fetch additional data from OMDB
    omdb_data = fetch_movie_data_from_omdb(imdb_id)
    movie.imdb_rating = omdb_data.get('imdb_rating')
    movie.rotten_tomatoes_rating = omdb_data.get('rotten_tomatoes_rating')
    movie.metacritic_rating = omdb_data.get('metacritic_rating')
    movie.director = omdb_data.get('director')
    movie.actors = omdb_data.get('actors')
    movie.mpa_rating = omdb_data.get('mpa_rating')
    movie.save()

    # Extract genres
    genres = movie_details.get('genres', [])        
    # Associate the movie with its genres from TMDB
    for genre_data in genres:
        genre, created = Genre.objects.get_or_create(name=genre_data['name'])
        movie.genres.add(genre)
    
    # Extract the streaming data
    streaming_data = movie_details.get('watch/providers', {}).get('results', {}).get('US', {}).get('flatrate', [])

    # If allowed_providers is None or empty, allow all providers
    if not allowed_providers:
        allowed_providers = [provider_data['provider_name'] for provider_data in streaming_data]

    # Loop through the streaming data and update the movie's streaming providers
    for provider_data in streaming_data:
        # Rename "Amazon Prime Video" to "Amazon Prime"
        provider_name = provider_data['provider_name']
        if provider_name == "Amazon Prime Video":
            provider_name = "Amazon Prime"

        # Check if the provider is in the allowed list
        if provider_name in filtered_providers:
            provider, created = StreamingProvider.objects.get_or_create(
                provider_id=provider_data['provider_id'],
                defaults={
                    'name': provider_name,
                    'logo_path': provider_data['logo_path'],
                }
            )
            movie.streaming_providers.add(provider)
    
    # Update the streaming providers using the JustWatch scraper for Tubi TV, Pluto TV, and Freevee
    movie.save()    # save before
    process_justwatch_streamers(movie)
    movie = Movie.objects.filter(title=movie.title, release_year=movie.release_year).first()    # open again after saving

    providers = movie.streaming_providers.all()
    sorted_providers = sorted(providers, key=lambda x: x.ranking)

    if sorted_providers:
        top_provider = sorted_providers[0]
        movie.top_streaming_providers.add(top_provider)

    # Fetch Letterboxd ratings data
    try:
        rating_data = lbd_scrape.get_rating(movie.title, movie.release_year)
        if rating_data:
            if isinstance(rating_data, dict):
                movie.letterboxd_rating = rating_data['Weighted Average']
            elif isinstance(rating_data, list): 
                movie.letterboxd_rating = rating_data[0]
    except Exception as e:
        print(f"Failure: {e}")

    movie.save()
    print(f"Movie '{movie.title}' (ID: {tmdb_id}) fetched and saved to the database.")


# Fetch detailed information about a movie from TMDB
def fetch_movie_details_from_tmdb(tmdb_id):
    # Define the TMDB API endpoint and parameters
    url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?language=en-US&append_to_response=videos,watch/providers,recommendations"
    # Fetch movie details, videos, and recommendations from TMDB
    response = requests.get(url, headers=HEADERS)
    return response.json()


# Fetch additional data about a movie from OMDB
def fetch_movie_data_from_omdb(imdb_id):
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
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
    movie_data['actors'] = data.get('Actors')
    movie_data['mpa_rating'] = data.get('Rated')
    return movie_data


# Fetch the trailer key for a movie from its video results
def fetch_movie_trailer_key(video_results):
    # Filter the results to get the trailer key
    for result in video_results:
        if result['type'].lower() == 'trailer':
            return result['key']
    return None


# Fetch popular movies from TMDB
def fetch_popular_movies(start_page=1, end_page=5):
    if end_page > 500:
        end_page = 500  # Limit the number of pages to 500

    total_num_movies = 20 * (end_page - start_page + 1)
    
    print(f"Fetching {total_num_movies} movies from TMDB")
    fetches_per_second = 20

    movies = Movie.objects.all()
    num_movies_in_db = movies.count()
    print(f"Movies in database: {num_movies_in_db}")
    
    # Semaphore to limit the number of concurrent API fetches
    semaphore = Semaphore(fetches_per_second)

    def fetch_movie(movie_data, page_num):
        movie_id = movie_data["id"]
        tmdb_popularity = movie_data["popularity"]

        # Check if the movie already exists in the database
        movie = Movie.objects.filter(tmdb_id=movie_id).first()
        
        # If the movie already exists in db, update its tmdb_popularity attribute
        if movie:
            movie.tmdb_popularity = tmdb_popularity
            movie.save()

        # Avoid obscure foreign films
        original_language = movie_data["original_language"]
        movie_title = movie_data["title"]
        if page_num > 40 and original_language != "en":
            print(f"Skipped {original_language} film: {movie_title} ")
            return

        with semaphore:
            # Ensure we don't make more than 20 requests per second
            time.sleep(1/fetches_per_second)  # sleep 50ms
            search_and_fetch_movie_by_id(movie_id)
    
    title = 'Fetching popular movies'
    for page_num in range(start_page, end_page + 1):
        index = (page_num - start_page + 1) * 20
        # Create a loading progress bar
        progress_bar_iteration(title, index, total_num_movies)
        
        url = f"{TMDB_BASE_URL}/movie/popular?language=en-US&page={page_num}"
        response = requests.get(url, headers=HEADERS)
        json_response = response.json()
        results = json_response['results']

        # Use a thread pool to process movies in parallel
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_movie, movie, page_num) for movie in results]
            for future in as_completed(futures):
                try:
                    # If the function returns a result, it will be available as future.result()
                    result = future.result()
                except Exception as e:
                    # Handle exception
                    print(f"An error occurred: {str(e)}")

    return json_response


# Fetch movies that are currently playing from TMDB
def fetch_now_playing_movies(start_page=1, end_page=5):
    # Set now_playing to False for all movies
    Movie.objects.update(now_playing=False)
    
    total_num_movies = 20 * (end_page - start_page + 1)
    
    # Semaphore to limit the number of concurrent API fetches
    semaphore = Semaphore(20)  # Allowing 20 fetches per second

    def process_movie(movie):
        with semaphore:
            # Ensure we don't make more than 20 requests per second
            time.sleep(1/20)  # sleep 50ms
            tmdb_id = movie.get('id')
            title = movie.get('title')
            # Process each movie using the process_movie_search function
            process_movie_search(tmdb_id, title, now_playing=True)
    
    title = 'Fetching now playing movies'
    for page_num in range(start_page, end_page + 1):
        index = (page_num - start_page + 1) * 20
        # Create a loading progress bar
        progress_bar_iteration(title, index, total_num_movies)
        
        url = f"{TMDB_BASE_URL}/movie/now_playing?language=en-US&page={page_num}"
        response = requests.get(url, headers=HEADERS)
        movies = response.json().get('results', [])

        # Use a thread pool to process movies in parallel
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_movie, movie) for movie in movies]
            for future in as_completed(futures):
                try:
                    # If the function returns a result, it will be available as future.result()
                    result = future.result()
                except Exception as e:
                    # Handle exception
                    print(f"An error occurred: {str(e)}")


# Fetch movies for the index page
def get_movies_for_index():
    # Fetch movies that are marked as now_playing
    now_playing_movies = Movie.objects.filter(now_playing=True)
    # Fetch 24 random movies from the now_playing movies for "New Movies"
    new_movies = random.sample(list(now_playing_movies), min(24, len(now_playing_movies)))
    
    # Order movies by tmdb_popularity in descending order, exclude the new movies, and take the top 200
    top_200_popular_movies = Movie.objects.exclude(id__in=[movie.id for movie in new_movies]).order_by(F('tmdb_popularity').desc(nulls_last=True))[:200]
    # Randomly select 24 movies from the top 200
    popular_movies = random.sample(list(top_200_popular_movies), min(24, len(top_200_popular_movies)))

    # Fetch the top 200 movies based on imdb_rating
    top_200_movies = Movie.objects.all().exclude(id__in=[movie.id for movie in new_movies] + [movie.id for movie in popular_movies]).order_by('-imdb_rating')[:200]
    # Randomly select 30 movies from the top 200
    top_rated_movies = random.sample(list(top_200_movies), min(30, len(top_200_movies)))
    # Sorts the selected 30 movies by their imdb_rating, with None values at the end
    top_rated_movies.sort(key=lambda movie: (movie.imdb_rating is not None, movie.imdb_rating), reverse=True)
    
    # Fetch 120 random movies for "More Movies", excluding the ones already selected in new_movies, popular_movies, and top_rated_movies
    more_movies = Movie.objects.all().exclude(id__in=[movie.id for movie in new_movies] + [movie.id for movie in popular_movies] + [movie.id for movie in top_rated_movies]).order_by('?')[:120]
    
    return {
        'new_movies': new_movies,
        'popular_movies': popular_movies,
        'top_rated_movies': top_rated_movies,
        'more_movies': more_movies,
    }


# Helper function for update_streaming_providers()
def fetch_movie_streaming_data(movie, index):
    url = f"{TMDB_BASE_URL}/movie/{movie.tmdb_id}?language=en-US&append_to_response=watch/providers"
    response = requests.get(url, headers=HEADERS)
    response_data = response.json()
    return movie, response_data, index

# Update the streaming providers for all movies in the Movie database
def update_streaming_providers(test_limit=None, exclude_non_null_jw_url=False):
    # test_limit = 10   # Test mode, quantity of test cases
    process_justwatch = False           # Takes a while. Process JustWatch data for Tubi TV, Pluto TV, and Freevee
    exclude_non_null_jw_url = False     # Filter only movies with null JW Urls
    include_2024 = True    # Null JW Urls are commonly 2024 before the movie is available
    if test_limit:
        # movies = list(Movie.objects.all()[:test_limit])
        previous = 0
        new_limit = test_limit + previous
        movies = list(Movie.objects.all()[previous:new_limit])
    else:
        # movies = list(Movie.objects.order_by('-created_at')[:10])
        movies = list(Movie.objects.all())

    if exclude_non_null_jw_url:
        filtered_movies = [
            movie for movie in movies 
            if (not movie.justwatch_url) and (include_2024 or movie.release_year != 2024)
        ]
        movies = filtered_movies

    print(f'Total movies to update: {len(movies)}')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  # Limit to 20 threads
        futures = [executor.submit(fetch_movie_streaming_data, movie, index) for index, movie in enumerate(movies)]

        for future in concurrent.futures.as_completed(futures):
            movie, response_data, index = future.result()  # Unpack the results

            # Clear all streaming providers except Tubi TV, Pluto TV, and Freevee
            current_providers = movie.streaming_providers.all()
            for provider in current_providers:
                if provider.name not in ['Tubi TV', 'Pluto TV', 'Freevee']:
                    movie.streaming_providers.remove(provider)
                    
            streaming_data = response_data.get('watch/providers', {}).get('results', {}).get('US', {}).get('flatrate', [])
            # Update streaming providers based on the fetched data
            for provider_data in streaming_data:
                # Rename "Amazon Prime Video" to "Amazon Prime"
                provider_name = provider_data['provider_name']
                if provider_name == "Amazon Prime Video":
                    provider_name = "Amazon Prime"

                # Check if the provider is in the allowed list
                if provider_name in filtered_providers:
                    provider, created = StreamingProvider.objects.get_or_create(
                        provider_id=provider_data['provider_id'],
                        defaults={
                            'name': provider_name,
                            'logo_path': provider_data['logo_path'],
                        }
                    )
                    movie.streaming_providers.add(provider)

            if process_justwatch:
                # Remove Tubi TV, Pluto TV, and Freevee before calling process_justwatch_streamers
                current_providers = movie.streaming_providers.all()
                for provider in current_providers:
                    if provider.name in ['Tubi TV', 'Pluto TV', 'Freevee']:
                        movie.streaming_providers.remove(provider)

                # Update the streaming providers using the JustWatch scraper for Tubi TV, Pluto TV, and Freevee
                process_justwatch_streamers(movie, add_delay=True)

            providers = movie.streaming_providers.all()
            sorted_providers = sorted(providers, key=lambda x: x.ranking)
            movie.top_streaming_providers.clear()

            if sorted_providers:
                top_provider = sorted_providers[0]
                movie.top_streaming_providers.add(top_provider)

            if index % 10 == 0 and index != 0:
                print(f'Updated streaming providers for {index}/{len(movies)} movies')
    executor.shutdown()  # Ensure that the executor is closed after completing all tasks


# Helper function for update_omdb_movie_ratings()
def fetch_and_update_omdb_movie_ratings(movie):
    try:
        omdb_data = fetch_movie_data_from_omdb(movie.imdb_id)

        if omdb_data.get('imdb_rating'):
            movie.imdb_rating = omdb_data['imdb_rating']
        if omdb_data.get('rotten_tomatoes_rating'):
            movie.rotten_tomatoes_rating = omdb_data['rotten_tomatoes_rating']
        if omdb_data.get('metacritic_rating'):
            movie.metacritic_rating = omdb_data['metacritic_rating']
        with database_lock:
            movie.save()
    except Exception as e:
        print(f"Error updating omdb ratings for movie '{movie.title}': {e}")

# Update the IMDB, RT, and Metacritic ratings for all movies in the Movie database
def update_omdb_movie_ratings(test_limit=None):
    # test_limit = 40   # Test mode, quantity of test cases
    if test_limit:
        movies = Movie.objects.all()[:test_limit]
    else:
        movies = Movie.objects.all()

    total_movies = len(movies)
    print(f'Total movies in database: {total_movies}')

    # Limit the number of concurrent requests to 20
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Submit fetch_and_update_omdb_movie_ratings for each movie to the executor
        futures = [executor.submit(fetch_and_update_omdb_movie_ratings, movie) for movie in movies]

        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            future.result()  # Wait for the result, but ignore it
            
            # Print progress at regular intervals
            if index % 100 == 0 or index == total_movies:
                print(f'Updated omdb ratings for {index}/{total_movies} movies')


# Updates the movie recommendations for all movies in the Movie database
def update_movie_recommendations():
    # Get all movies from your database
    movies = Movie.objects.all()
    total_num_movies = movies.count()
    
    # Print the number of movies in the database
    print(f'Total movies in database: {movies.count()}')

    for index, movie in enumerate(movies, start=1):
        # Define the TMDB API endpoint and parameters for fetching recommendations
        
        # Create a loading progress bar
        title = 'Updating Movie Recs'
        progress_bar_iteration(title, index, total_num_movies)
        
        url = f"{TMDB_BASE_URL}/movie/{movie.tmdb_id}/recommendations?language=en-US"

        # Fetch movie recommendations from TMDB
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        except requests.RequestException as e:
            print(f"Failed to fetch recommendations for movie '{movie.title}' (ID: {movie.tmdb_id}): {e}")
            continue  # Skip to the next movie
        
        recommendations = response.json().get('results', [])
        
        # Clear the existing recommendations
        movie.recommended_movie_data.clear()
        
        for recommendation in recommendations:
            recommended_tmdb_id = recommendation.get('id')
            recommended_title = recommendation.get('title')
            recommended_popularity = recommendation.get('popularity', 0)  # Default to 0 if popularity is not present

            # Only append the recommendation if its popularity is greater than 10
            if recommended_popularity > 10:
                movie.recommended_movie_data.append({
                    'tmdb_id': recommended_tmdb_id,
                    'title': recommended_title,
                    'tmdb_popularity': recommended_popularity  # Store the tmdb_popularity here
                })
        
        # Save the updated recommended_movie_data field to the database
        movie.save()
        
        # Print a message every 100 movies processed
        if index % 100 == 0:
            print(f'Processed recommendations for {index}/{movies.count()} movies')
        
    # After fetching TMDB recommendations
    if len(movie.recommended_movie_data) < 20:

        # Calculate number of recommendations needed
        needed = 20 - len(movie.recommended_movie_data)

        # Query for recent movies in database
        recent_movies = Movie.objects.order_by('-created_at')[:needed*2]
        
        for r_movie in recent_movies:
            if len(movie.recommended_movie_data) >= 20:
                break

            movie.recommended_movie_data.append({
                'tmdb_id': r_movie.tmdb_id,
                'title': r_movie.title, 
                'tmdb_popularity': r_movie.tmdb_popularity
            })
            
            # Save updated recommendations 
            movie.save()

# Update the streaming providers using the JustWatch scraper for Tubi TV, Pluto TV, and Freevee
def process_justwatch_streamers(movie, add_delay=False):
    movie_instance = Movie.objects.filter(title=movie.title, release_year=movie.release_year).first()
    if movie_instance:
        providers, jw_url_movie = jw_scrape.fetch_justwatch(movie, add_delay)
        movie_instance.justwatch_url = jw_url_movie
        movie_instance.save()
        if providers is not None:
            for provider_name in providers:
                if provider_name in ["Tubi TV", "Pluto TV", "Freevee"]:
                    # Get or create a StreamingProvider instance for the current provider
                    streaming_provider, _ = StreamingProvider.objects.get_or_create(name=provider_name)
                    movie_instance.streaming_providers.add(streaming_provider)
            
            movie_instance.save()
    else:
        print(f"Movie not found in the database: {movie.title}, {movie.release_year}")

# Update the Letterboxd ratings for all movies in the Movie database
def update_letterboxd_ratings(update_movie=None):
    ''' Update the letterboxd ratings for all movies in the Movie database ''' 
    exclude_non_null_lbd_url = False
    
    # Get movies
    movies = Movie.objects.all()  
    if exclude_non_null_lbd_url:
        movies = movies.filter(letterboxd_url__isnull=True)
    if update_movie:
        # Filter movies based on the update_movie argument, from the testforwebscaper and update_webscraper_url views
        title = update_movie.title
        release_year = update_movie.release_year
        movies = movies.filter(title__icontains=title, release_year=release_year)
        
    # Limiter for calls; try to not overload Letterboxd
    request_frequency = 8
    sleep_time = 1/request_frequency

    # Start time
    start_ts = time.time()
    start_dt = datetime.datetime.fromtimestamp(start_ts)
    print("Start:", start_dt)
 
    # Calculate totals
    total_movies = len(movies)
    ratings_per_sec = 7.85
    total_secs = int(total_movies / ratings_per_sec)
  
    print(f"Total movies: {total_movies}")
    print(f"Total estimated time: {seconds_to_readable_time(total_secs)}")

    # Calculate completion datetime
    delta = datetime.timedelta(seconds=total_secs)
    completion_dt = start_dt + delta

    print("Estimated completion:", completion_dt)

    # Updates the movie with letterboxd rating
    def iterate_movie(movie):
        try:
            # Try to get rating information using letterboxd web scraper
            rating_dict = lbd_scrape.get_rating(movie.title, movie.release_year)

            # If rating dict exists, append information to movie model, otherwise fail
            if rating_dict:
                movie.letterboxd_rating = rating_dict["Weighted Average"]
                # TODO: Add histogram weights or remove this line
                # movie.letterboxd_histogram_weights = rating_dict["Histogram Weights"]
                if "Letterboxd URL" in rating_dict:
                    movie.letterboxd_url = rating_dict.get("Letterboxd URL")
            else:
                raise Exception

            # print("Successful scrape of letterboxd for", movie.title, "("+str(movie.release_year)+")")
        except Exception as e:
            print("Failed Letterboxd scrape for", movie.title, "("+str(movie.release_year)+")")
            
        # Save the updated recommended_movie_data field to the database
        movie.save()

    # Make API Calls to update each movie
    threads = []
    for index, movie in enumerate(movies, start=1):
        thread = threading.Thread(target=iterate_movie, args=(movie, ))
        
        # Create a loading progress bar
        title = 'Letterboxd Scraping Progress'
        progress_bar_iteration(title, index, total_movies)
        
        threads.append(thread)
        thread.start()
        time.sleep(sleep_time)
        
    # Wait until all threads are done
    for thread in threads:
        thread.join()

    # End time
    end_ts = time.time()
    end_dt = datetime.datetime.fromtimestamp(end_ts)

    print("End:", end_dt)
    
    # Calculate duration
    duration = end_dt - start_dt

    # Format duration
    duration_secs = duration.total_seconds()
    fmt_duration = time.strftime('%H:%M:%S', time.gmtime(duration_secs))

    print(f"Total duration: {fmt_duration}")


# Fetches pages from the TMDb API for Discover movies
def fetch_tmdb_discover_movies(start_page=1, end_page=10):
    total_num_movies = 20 * (end_page - start_page + 1)
    
    print(f"Fetching {total_num_movies} movies from TMDB")
    fetches_per_second = 20

    movies = Movie.objects.all()
    num_movies_in_db = movies.count()
    print(f"Movies in database: {num_movies_in_db}")
    
    # Semaphore to limit the number of concurrent API fetches
    semaphore = Semaphore(fetches_per_second)

    def process_movie(movie):
        with semaphore:
            # Ensure we don't make more than 20 requests per second
            time.sleep(1/fetches_per_second)  # sleep 50ms
            tmdb_id = movie.get('id')
            title = movie.get('title')
            # Process each movie using the process_movie_search function
            process_movie_search(tmdb_id, title)

    for page in range(start_page, end_page + 1):
        index = (page - start_page + 1) * 20
        # Create a loading progress bar
        title = 'Fetching TMDb discover movies'
        progress_bar_iteration(title, index, total_num_movies)

        url = f"{TMDB_BASE_URL}/discover/movie?sort_by=popularity.desc&language=en-US&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        movies = response.json().get('results', [])
        
        # Use a thread pool to process movies in parallel
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_movie, movie) for movie in movies]
            for future in as_completed(futures):
                try:
                    # If the function returns a result, it will be available as future.result()
                    result = future.result()
                except Exception as e:
                    # Handle exception
                    print(f"An error occurred: {str(e)}")


def get_refreshed_movie_data(movie_tmdb_id):
    movie, created = Movie.objects.get_or_create(tmdb_id=movie_tmdb_id)
    
    if created:
        print(f"New movie created with tmdb_id: {movie_tmdb_id}")
    else:
        print(f"Updating existing movie with tmdb_id: {movie_tmdb_id}")

    # Make an API call to fetch more details about the movie from TMDB
    movie_details = fetch_movie_details_from_tmdb(movie.tmdb_id)

    print(f"\nRefreshed movie data: {movie.title} (tmdb_id: {movie.tmdb_id})")
    formatted_last_updated = movie.last_updated.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Last updated: {formatted_last_updated}")
    print(f"Before IMDb ratings: {movie.imdb_rating}")
    print(f"Before Letterboxd ratings: {movie.letterboxd_rating}/5")
    print(f"Before Rotten Tomatoes ratings: {movie.rotten_tomatoes_rating}")
    print(f"Before Metacritic ratings: {movie.metacritic_rating}")

    # Retrieve and format streaming provider names
    streaming_providers = movie.streaming_providers.all()
    provider_names = [provider.name for provider in streaming_providers]
    providers_string = ", ".join(provider_names)
    # Print the formatted list of streaming providers
    print(f"Before Streaming providers: {providers_string}\n")

    # Check if the movie is adult content
    if movie_details.get('adult'):
        return

    # Update movie details
    movie.title = movie_details.get('title')
    movie.imdb_id = movie_details.get('imdb_id')
    movie.overview = movie_details.get('overview')
    movie.poster_path = movie_details.get('poster_path')
    # release_date = movie_details.get('release_date')
    movie.release_year = int(movie_details.get('release_date', '').split('-')[0]) if movie_details.get('release_date') else None
    movie.runtime = movie_details.get('runtime')
    movie.tagline = movie_details.get('tagline')
    movie.trailer_key = fetch_movie_trailer_key(movie_details.get('videos', {}).get('results', []))
    movie.now_playing = movie.release_year in [2023, 2024]
    
    # Verify now_playing is either 2023 or 2024
    movie.now_playing = True
    if movie.release_year not in [2023, 2024]:
        movie.now_playing = False 

    movie.save()

    # Extract recommendations
    recommendations = movie_details.get('recommendations', {}).get('results', [])
    recommended_movie_data = []
    for rec in recommendations:
        rec_popularity = rec.get('popularity', 0)  # Default to 0 if popularity is not present
        if rec_popularity > 3:
            recommended_movie_data.append({
                'tmdb_id': rec.get('id'),
                'title': rec.get('title'),
                'tmdb_popularity': rec_popularity  # Store the tmdb_popularity here
            })

    movie.recommended_movie_data = recommended_movie_data

    # Make an API call to fetch more details about the movie from OMDB    
    omdb_data = fetch_movie_data_from_omdb(movie.imdb_id)
    movie.imdb_rating = omdb_data.get('imdb_rating')
    movie.rotten_tomatoes_rating = omdb_data.get('rotten_tomatoes_rating')
    movie.metacritic_rating = omdb_data.get('metacritic_rating')
    movie.director = omdb_data.get('director')
    movie.actors = omdb_data.get('actors')
    movie.mpa_rating = omdb_data.get('mpa_rating')
    movie.save()

    # Extract genres
    genres = movie_details.get('genres', [])        
    # Associate the movie with its genres from TMDB
    for genre_data in genres:
        genre, created = Genre.objects.get_or_create(name=genre_data['name'])
        movie.genres.add(genre)
    
    # Extract the streaming data
    streaming_data = movie_details.get('watch/providers', {}).get('results', {}).get('US', {}).get('flatrate', [])
    movie.streaming_providers.clear()
    movie.top_streaming_providers.clear()
    allowed_providers = filtered_providers
    # If allowed_providers is None or empty, allow all providers
    if not allowed_providers:
        allowed_providers = [provider_data['provider_name'] for provider_data in streaming_data]

    # Loop through the streaming data and update the movie's streaming providers
    for provider_data in streaming_data:
        # Rename "Amazon Prime Video" to "Amazon Prime"
        provider_name = provider_data['provider_name']
        if provider_name == "Amazon Prime Video":
            provider_name = "Amazon Prime"

        # Check if the provider is in the allowed list
        if provider_name in allowed_providers:
            provider, created = StreamingProvider.objects.get_or_create(
                provider_id=provider_data['provider_id'],
                defaults={
                    'name': provider_name,
                    'logo_path': provider_data['logo_path'],
                }
            )
            movie.streaming_providers.add(provider)

    # Update the streaming providers using the JustWatch scraper for Tubi TV, Pluto TV, and Freevee
    movie.save()    # save before
    process_justwatch_streamers(movie)
    movie = Movie.objects.filter(title=movie.title, release_year=movie.release_year).first()    # open again after saving

    providers = movie.streaming_providers.all()
    sorted_providers = sorted(providers, key=lambda x: x.ranking)

    if sorted_providers:
        top_provider = sorted_providers[0]
        movie.top_streaming_providers.add(top_provider)

    # Fetch Letterboxd ratings data
    try:
        rating_data = lbd_scrape.get_rating(movie.title, movie.release_year)
        if rating_data:
            if isinstance(rating_data, dict):
                movie.letterboxd_rating = rating_data['Weighted Average']
            elif isinstance(rating_data, list): 
                movie.letterboxd_rating = rating_data[0]
    except Exception as e:
        print(f"Failure: {e}")

    # Save refreshed movie data in the Movie database
    movie.save()

    # Print refreshed movie data
    formatted_last_updated = movie.last_updated.strftime('%Y-%m-%d %H:%M:%S')
    print(f'\nRefreshed movie data: {movie.title} (tmdb_id: {movie.tmdb_id})')
    print(f"Last updated: {formatted_last_updated}")
    print(f"After IMDb ratings: {movie.imdb_rating}")
    print(f"After Letterboxd ratings: {movie.letterboxd_rating}/5")
    print(f"After Rotten Tomatoes ratings: {movie.rotten_tomatoes_rating}")
    print(f"After Metacritic ratings: {movie.metacritic_rating}")

    # Retrieve and format streaming provider names
    streaming_providers = movie.streaming_providers.all()
    provider_names = [provider.name for provider in streaming_providers]
    providers_string = ", ".join(provider_names)
    # Print the formatted list of streaming providers
    print(f"After Streaming providers: {providers_string}\n")


def get_person_slugs(person_name):
    if person_name == "N/A":
        return []

    slug_list = []
    if person_name:
        temp_list = person_name.split(',')
        for person in temp_list:
            person = person.strip().replace('-', '--').replace(' ', '-')
            person_str = str(person)
            slug_list.append(person_str)
    return slug_list

def get_person_names(person_name):
    if person_name == "N/A":
        return []
    
    name_list = []
    if person_name:
        temp_list = person_name.split(',')
        for person in temp_list:
            person = person.strip().replace(',', '')
            name_list.append(person)
    return name_list

def get_movies_by_director(director_name):
    # Query for movies containing the director's name
    movies = Movie.objects.filter(director__icontains=director_name).order_by('release_date')
    return movies

def get_movies_by_actor(actor_name):
    # Query for movies containing the director's name
    movies = Movie.objects.filter(actors__icontains=actor_name).order_by('release_date')
    return movies

def get_person_id(actor_name):
    search_url = f"{TMDB_BASE_URL}/search/person?query={actor_name}&include_adult=false&language=en-US&page=1"
    response = requests.get(search_url, headers=HEADERS)
    data = response.json()
    if data.get('results'):
        actor = data['results'][0]
        return actor['id']
    else:
        return None

def get_movies_from_tmdb_by_actor(person_id):
    credits_url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits"
    response = requests.get(credits_url, headers=HEADERS)
    data = response.json()
    movie_ids = [credit['id'] for credit in data.get('cast', [])]
    # Filter movies by IDs found in the database
    movies = Movie.objects.filter(tmdb_id__in=movie_ids).order_by('release_date')
    return movies

def get_director_movies_from_tmdb_to_fetch(person_id):
    credits_url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits"
    response = requests.get(credits_url, headers=HEADERS)
    data = response.json()
    
    # Filter movies by crew where the person is a director and the movie has a release date
    director_movie_ids = []
    for crew_member in data.get('crew', []):
        if crew_member.get('job') == 'Director' and crew_member.get('release_date'):
            director_movie_ids.append(crew_member['id'])
    
    return director_movie_ids

def get_actor_movies_from_tmdb_to_fetch(person_id):
    credits_url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits"
    response = requests.get(credits_url, headers=HEADERS)
    data = response.json()
    
    # Filter movies by cast where the person is an actor and the movie has a release date and popularity above 5
    actor_movie_ids = []
    for cast_member in data.get('cast', []):
        if cast_member['order'] < 2 and cast_member.get('release_date') and cast_member.get('popularity', 0) > 5:
            actor_movie_ids.append(cast_member['id'])
    
    return actor_movie_ids

# Performs filtering to the movie ratings list
def filter_ratings(movie_ratings, rating_begin, rating_end):
    if rating_begin is not None and rating_end is not None:
        movie_ratings = movie_ratings.filter(user_rating__range=(rating_begin, rating_end))
    return movie_ratings

# Performs filtering to the movies list
def filter_movies(movies, genres, streamers, year_begin, year_end, imdb_begin, imdb_end):
    # Fitler for Genre
    if genres is not None:
        movies = movies.filter(genres__in=genres)

    # Filter for Streaming Providers
    if streamers is not None:
        movies = movies.filter(streaming_providers__in=streamers)

    # Filter for release year
    if year_begin is not None and year_end is not None:
        movies = movies.filter(release_year__range=(year_begin, year_end))

    # Filter for IMDB rating
    if imdb_begin is not None and imdb_end is not None:
        if float(imdb_begin) != 0.0 or float(imdb_end) != 10.0:
            movies = movies.filter(imdb_rating_num__isnull=False, imdb_rating_num__range=(imdb_begin, imdb_end))
        else:
            movies = movies.filter(Q(imdb_rating_num__range=(imdb_begin, imdb_end)) | Q(imdb_rating_num=None))

    return movies.distinct()

# Get FilmFocus rating string for movie details page
def get_filmfocus_rating(movie):
    ratings = MovieRating.objects.filter(movie=movie)
    if not ratings.exists():
        return None
    average_rating = ratings.aggregate(Avg('user_rating'))['user_rating__avg']
    num_reviews = ratings.count()
    formatted_num_reviews = "{:,}".format(num_reviews)  # Format with commas ex: 1,234
    return f"{average_rating:.1f}/10 ({formatted_num_reviews} {'review' if num_reviews == 1 else 'reviews'})"

def get_logged_in_user_profile_picture(request):
    """Retrieve the profile picture filename for the logged-in user."""
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        return user_profile.profile_pic
    else:
        return None


# Clear all movies from the database except for those in watchlist entries and movie ratings
def clear_movie_database():
    # Get all the titles and tmdb_ids of movies used in watchlist entries
    watchlist_movies = WatchlistEntry.objects.values_list('movie__title', 'movie__tmdb_id')
    
    # Get all the titles and tmdb_ids of movies with ratings
    rated_movies = MovieRating.objects.values_list('movie__title', 'movie__tmdb_id')
    
    # Combine the two sets of saved movies
    saved_movies = set(watchlist_movies) | set(rated_movies)

    # Query for movies to delete, excluding the saved ones
    movies_to_delete = Movie.objects.exclude(
        models.Q(title__in=[movie[0] for movie in saved_movies]) &
        models.Q(tmdb_id__in=[movie[1] for movie in saved_movies])
    )

    # Delete the movies
    deleted_count, _ = movies_to_delete.delete()
    print(f"{deleted_count} movies deleted from the database.")

# Handle the test for ban page to easily find bannable movies
def handle_test_for_ban(start_date, end_date):
    movies_to_display = Movie.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    return movies_to_display

# Handle the test display page
def handle_test_display_page(fetch_movies_count=10):
    movies_to_display = Movie.objects.all().order_by('?')[:fetch_movies_count]
    return movies_to_display
