"""
Name of code artifact: services.py
Brief description: Contains business logic for the FilmFocus web application, including functions to fetch movie details from TMDB and OMDB, and to manage the movie database.
Programmer’s name: Mark
Date the code was created: 09/18/2023
Dates the code was revised: 09/21/2023
Brief description of each revision & author: Initialized code and basic functions (Mark)
Preconditions: Django environment must be set up correctly, and necessary environment variables (API keys) must be available.
Acceptable and unacceptable input values or types: Functions expect specific types as documented in their respective comments.
Postconditions: Functions return values or modify the database as per their documentation.
Return values or types: Varies based on the function.
Error and exception condition values or types that can occur: Errors can occur if API limits are reached or if there are issues with the database.
Side effects: Some functions modify the database.
Invariants: None.
Any known faults: None.
"""

from webapp.models import *
import requests
import json
from dotenv import load_dotenv
import os
import random
from django.db.models import F
import webapp.letterboxd_scraper as lbd_scrape
import threading
import time
import datetime


# Load environment variables
load_dotenv()
OMDB_API_KEY = os.environ["OMDB_API_KEY"]               # limited to 100,000 calls/day
TMDB_API_KEY_STRING = os.environ["TMDB_API_KEY_STRING"] # limited to around 50 calls/second
MASTER_LIST = "webapp/data/tmdb_master_movie_list.json"
ALLOWED_PROVIDERS_LIST = "webapp/data/allowed_providers_list.txt"

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


# Search for a movie by its title
def search_movie_by_title(title):
    return title_to_id_dict.get(title.lower())


# Search for a movie by its TMDB ID
def search_movie_by_id(tmdb_id):
    return id_to_title_dict.get(tmdb_id)


# Search for a movie by its title and fetch its details
def search_and_fetch_movie_by_title(title):
    tmdb_id = search_movie_by_title(title)
    process_movie_search(tmdb_id, title)


# Search for a movie by its TMDB ID and fetch its details
def search_and_fetch_movie_by_id(tmdb_id):
    title = search_movie_by_id(tmdb_id)
    process_movie_search(tmdb_id, title)


# Retrieve the watchlists for a user
def get_watchlists_for_user(user):
    watchlists = Watchlist.objects.filter(user=user)
    return watchlists

# Progress bar for a given function
def progress_bar(title, current, total, bar_length=100):
    percent = float(current) * 100 / total
    arrow   = '=' * int(percent/100 * bar_length - 1) + '>'
    spaces  = ' ' * (bar_length - len(arrow))
    print(f'\r{title}: [{arrow}{spaces}] {percent:.0f}%  ', end='\r')
    if current == total: 
        print(f'\r{title}: [{arrow}{spaces}] {percent:.0f}%  ', end='\n')

# Progress bar handler, if wait is iteration-based    
def wait_iteration(title, current, num_iterations):
    progress_bar(title, current, num_iterations, bar_length=100)
    
# Progress bar handler, if wait is time-based    
def wait_time(title, wait_seconds):
    count = 0
    while count < (wait_seconds + 1):
        count += 1
        progress_bar(title, count, wait_seconds, bar_length=100)
        time.sleep(1)
    # print()     # formatting for the progress bar


# Timer for testing funtions
def timer(function_name, fetch_func, args):
    ''' Timer function to print out the time elapsed for each function call. '''

    start_time = time.time()
    start_time_readable = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
    print(f'Start {function_name}: {start_time_readable}')

    movies = fetch_func(**args) # Call the function here, currently don't do anythin with the output

    end_time = time.time()
    end_time_readable = datetime.datetime.fromtimestamp(end_time).strftime('%H:%M:%S')  

    total_time_secs = end_time - start_time

    # Convert seconds to HH:MM:SS
    hours, remainder = divmod(total_time_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_time_readable = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

    print(f'Finished {function_name}: {end_time_readable}')
    print(f'Total time for {function_name}: {total_time_readable}.')


# Process the search results for a movie and fetch its details
def process_movie_search(tmdb_id, title, now_playing=False, allowed_providers=filtered_providers):
    # Check if the movie is in the TMDB master list
    if not tmdb_id:
        print(f"Movie '{title}' not found in the master list.")
        return
    
    # Check if the movie is in the ban list
    if str(tmdb_id) in BAN_LIST:
        # print(f"Movie '{title}' (ID: {tmdb_id}) is in the ban list and was not added.") # TODO: leave here, switch depending on what you want to display
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
        # print(f"Movie '{title}' (ID: {tmdb_id}) already exists in the database.") # TODO: leave here, switch depending on what you want to display
        return

    # Make an API call to fetch more details about the movie from TMDB
    movie_details = fetch_movie_details_from_tmdb(tmdb_id)
    
    # Check if the movie is adult content
    if movie_details.get('adult'):
        # print(f"Movie '{title}' (ID: {tmdb_id}) is for adults and was not added.") # TODO: leave here, switch depending on what you want to display
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
        release_year=release_year,
        runtime=movie_details.get('runtime'),
        tagline=movie_details.get('tagline'),
        trailer_key=trailer_key,
        now_playing=now_playing,
    )
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

    # Fetch additional data from OMDB
    omdb_data = fetch_movie_data_from_omdb(imdb_id)
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
    
    # Extract the streaming data
    streaming_data = movie_details.get('watch/providers', {}).get('results', {}).get('US', {}).get('flatrate', [])

    # If allowed_providers is None or empty, allow all providers
    if not allowed_providers:
        allowed_providers = [provider_data['provider_name'] for provider_data in streaming_data]

    # Loop through the streaming data and update the movie's streaming providers
    for provider_data in streaming_data:
        # Check if the provider is in the allowed list
        if provider_data['provider_name'] in allowed_providers:
            provider, created = StreamingProvider.objects.get_or_create(
                provider_id=provider_data['provider_id'],
                defaults={
                    'name': provider_data['provider_name'],
                    'logo_path': provider_data['logo_path'],
                }
            )
            movie.streaming_providers.add(provider)

    # Fetch Letterboxd ratings data
    try:
        rating_dict = lbd_scrape.get_rating(movie.title, movie.release_year)    # TODO: Verify implemention
        if rating_dict:
            movie.letterboxd_rating = rating_dict["Weighted Average"]
    except Exception as e:
        print(f"Failure: {e}")

    movie.save()
    print(f"Movie '{title}' (ID: {tmdb_id}) fetched and saved to the database.")  # TODO: leave here, switch depending on what you want to display


# Fetch detailed information about a movie from TMDB
def fetch_movie_details_from_tmdb(tmdb_id):
    # Define the TMDB API endpoint and parameters
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US&append_to_response=videos,watch/providers,recommendations"
    headers = {
        "accept": "application/json",
        'Authorization': TMDB_API_KEY_STRING,
    }
    # Fetch movie details, videos, and recommendations from TMDB
    response = requests.get(url, headers=headers)
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
    movie_data['domestic_box_office'] = data.get('BoxOffice')
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
    total_num_movies = 20 * (end_page - start_page + 1)
    
    for page_num in range(start_page, end_page + 1):
        index = (page_num + 1) * 20
        # Create a loading progress bar
        title = f'  Fetching popular movies'
        wait_iteration(title, index, total_num_movies)
        
        # print(f"")
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
                    
    return json_response


# Fetch movies that are currently playing from TMDB
def fetch_now_playing_movies(start_page=1, end_page=5):
    # Set now_playing to False for all movies
    Movie.objects.update(now_playing=False)
    
    total_num_movies = 20 * (end_page - start_page + 1)
    
    for page_num in range(start_page, end_page + 1):  # Fetch the first 10 pages
        # print(f"Fetching now playing movies page number")   # TODO: leave here, switch depending on what you want to display
        
        index = (page_num + 1) * 20
        # Create a loading progress bar
        title = f'  Fetching now playing movies'
        wait_iteration(title, index, total_num_movies)
        
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


# Fetch movies for the index page
def get_movies_for_index():
    # Fetch movies that are marked as now_playing
    now_playing_movies = Movie.objects.filter(now_playing=True)
    # Fetch 16 random movies from the now_playing movies for "New Movies"
    new_movies = random.sample(list(now_playing_movies), min(16, len(now_playing_movies)))
    
    # Order movies by tmdb_popularity in descending order, exclude the new movies, and take the top 100
    top_100_popular_movies = Movie.objects.exclude(id__in=[movie.id for movie in new_movies]).order_by(F('tmdb_popularity').desc(nulls_last=True))[:100]
    # Randomly select 6 movies from the top 100
    popular_movies = random.sample(list(top_100_popular_movies), min(6, len(top_100_popular_movies)))

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


# Update the streaming providers for all movies in the Movie database
def update_streaming_providers():
    # Fetch all movies from your database
    movies = Movie.objects.all()
    total_num_movies = movies.count()

    # Print the number of movies in the database
    print(f'Total movies in database: {movies.count()}')

    for index, movie in enumerate(movies, start=1):
        # Define the TMDB API endpoint and parameters
        
        # Create a loading progress bar
        wait_iteration('  Updating Streaming Providers', index, total_num_movies)
        
        url = f"https://api.themoviedb.org/3/movie/{movie.tmdb_id}?language=en-US&append_to_response=watch/providers"
        headers = {
            "accept": "application/json",
            'Authorization': TMDB_API_KEY_STRING,
        }
        # Fetch movie details and streaming providers from TMDB
        response = requests.get(url, headers=headers)
        response_data = response.json()
        streaming_data = response_data.get('watch/providers', {}).get('results', {}).get('US', {}).get('flatrate', [])

        # Clear existing streaming providers for the movie
        movie.streaming_providers.clear()

        # Update streaming providers based on the fetched data
        for provider_data in streaming_data:
            # Check if the provider is in the filtered_providers list
            if provider_data['provider_name'] in filtered_providers:
                provider, created = StreamingProvider.objects.get_or_create(
                    provider_id=provider_data['provider_id'],
                    defaults={
                        'name': provider_data['provider_name'],
                        'logo_path': provider_data['logo_path'],
                    }
                )
                movie.streaming_providers.add(provider)

        # Print a message every 100 movies updated
        if index % 100 == 0:
            print(f'Updated streaming providers for {index}/{movies.count()} movies')


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
        wait_iteration('  Updating Movie Recs', index, total_num_movies)
        
        url = f"https://api.themoviedb.org/3/movie/{movie.tmdb_id}/recommendations?language=en-US"
        headers = {
            "accept": "application/json",
            'Authorization': TMDB_API_KEY_STRING,
        }

        # Fetch movie recommendations from TMDB
        try:
            response = requests.get(url, headers=headers)
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

            # Only append the recommendation if its popularity is greater than 1
            if recommended_popularity > 3:
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


# Update the Letterboxd ratings for all movies in the Movie database
def update_letterboxd_ratings():
    ''' Update the letterboxd ratings for all movies in the Movie database ''' 
        
    # Limiter for calls; try to not overload Letterboxd
    request_frequency = 8
    sleep_time = 1/request_frequency

    # Start time
    start_ts = time.time()
    start_dt = datetime.datetime.fromtimestamp(start_ts)

    print("Start:", start_dt)
    
    # Get movies
    movies = Movie.objects.all()  

    # Calculate totals
    total_movies = len(movies)
    ratings_per_sec = 10
    total_secs = total_movies / ratings_per_sec
  
    print(f"Total movies: {total_movies}")
    print(f"Total estimated secs: {total_secs}")

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
            else:
                raise Exception

            # Print Success
            # print("Successful scrape of letterboxd for", movie.title, "("+str(movie.release_year)+")")    # TODO: uncomment this line
        except Exception as e:
            # Print Failure
            print("Failed Letterboxd scrape for", movie.title, "("+str(movie.release_year)+")")          # TODO: uncomment this line
            

        # Save the updated recommended_movie_data field to the database
        movie.save()

    # Make API Calls to update each movie
    threads = []
    for index, movie in enumerate(movies, start=1):
        thread = threading.Thread(target=iterate_movie, args=(movie, ))
        
        # Create a loading progress bar
        wait_iteration('  Letterboxd Scraping Progress', index, total_movies)
        
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


# Fetches pages from the TMDd API for Discover movies
def fetch_tmdb_discover_movies(start_page=1, end_page=50):
    for page in range(start_page, end_page + 1):
        url = f"https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&language=en-US&page={page}"
        headers = {
            "accept": "application/json",
            'Authorization': TMDB_API_KEY_STRING,
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx and 5xx)
        response_data = response.json()
        movies = response_data.get('results', [])
        
        for movie in movies:
            tmdb_id = movie.get('id')
            title = movie.get('title')
            process_movie_search(tmdb_id, title)


# Clear all movies from the database
def clear_movie_database():
    deleted_count, _ = Movie.objects.all().delete()
    print(f"{deleted_count} movies deleted from the database.")


# Handle the test for ban page to easily find bannable movies
def handle_test_for_ban(start_date, end_date):
    movies_to_display = Movie.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
    return movies_to_display


# Handle the test display page and manage the movie database
def handle_test_display_page(settings):
    
    # 20 movies per page
    popular_pages = 5           # Number of popular pages from 1 to x with 20 results each, TMDb
    now_playing_pages = 5       # Number of now playing pages from 1 to x with 20 results each, TMDb
    fetch_movies_count = 10     # Number of individual movies returned to testdisplay, testdisplay/
    fetch_discover_count = 5    # Number of discover pages from 1 to x with 20 results each, TMDb
  
    # TODO: Implementation is in progress.  
    # movies_per_page = 20
    # pop_count = popular_pages * (1 + movies_per_page) # 1 for popular pages, 20 associated movie details.
    # iterations_count = popular_pages + now_playing_pages + fetch_movies_count + fetch_discover_count
    
    # Diplay the starting time of the test display page
    now_time = time.time()
    now_time_readable = datetime.datetime.fromtimestamp(now_time).strftime('%H:%M:%S')
    print(f'Starting test display page at {now_time_readable}\n')
    
    
    test_mode = True
    if test_mode: # test_mode == True
        ''' Test mode (ON). Tests the times and data for the various functions. '''
        
        if settings[0]:
            # clear_movie_database()  # deletes all entries in the movie database, USE WITH CAUTION
            timer(function_name='clear_movie_database', fetch_func=clear_movie_database, args={})

        if settings[1]:
            # fetch_popular_movies(1, end_page=popular_pages)
            # fetch_now_playing_movies(1, end_page=now_playing_pages)  # Fetch now playing movies after initializing the database
            timer(function_name='fetch_popular_movies', fetch_func=fetch_popular_movies, args={'start_page': 1, 'end_page': popular_pages})
            timer(function_name='fetch_now_playing_movies', fetch_func=fetch_now_playing_movies, args={'start_page': 1, 'end_page': now_playing_pages })
        elif settings[2]:  # Use 'elif' to ensure it doesn't run again if initialize_database is True
            # fetch_now_playing_movies(1, end_page=now_playing_pages)
            timer(function_name='fetch_now_playing_movies', fetch_func=fetch_now_playing_movies, args={'start_page': 1, 'end_page': now_playing_pages})
        
        if settings[3]:
            # update_streaming_providers()
            timer(function_name='update_streaming_providers', fetch_func=update_streaming_providers, args={})
        
        if settings[4]:
            # update_movie_recommendations()
            timer(function_name='update_movie_recommendations', fetch_func=update_movie_recommendations, args={})
        
        if settings[5]:
            # fetch_tmdb_discover_movies(1, end_page=fetch_discover_count)
            timer(function_name='fetch_tmdb_discover_movies', fetch_func=fetch_tmdb_discover_movies, args={'start_page': 1, 'end_page': fetch_discover_count})

        if settings[6]:
            # update_letterboxd_ratings()
            timer(function_name="update_letterboxd_ratings", fetch_func=update_letterboxd_ratings, args={})
    else: # test_mode == False
        ''' Test mode (OFF). '''
        
        if settings[0]:
            clear_movie_database()  # deletes all entries in the movie database, USE WITH CAUTION

        if settings[1]:
            fetch_popular_movies(1, end_page=popular_pages)
            fetch_now_playing_movies(1, end_page=now_playing_pages)  # Fetch now playing movies after initializing the database
        elif settings[2]:  # Use 'elif' to ensure it doesn't run again if initialize_database is True
            fetch_now_playing_movies(1, end_page=now_playing_pages)
        
        if settings[3]:
            update_streaming_providers()
        
        if settings[4]:
            update_movie_recommendations()
        
        if settings[5]:
            fetch_tmdb_discover_movies(1, end_page=fetch_discover_count)

        if settings[6]:
            update_letterboxd_ratings()
    
    # Prints which settings are set
    print(f"==========================")
    flags = ['erase_movie_db', 
             'init_movie_db', 
             'get_now_playing', 
             'update_streaming', 
             'update_recs',
             'get_discover_movies', 
             'update_letterboxd_ratings',
             ]
    for index, flag in enumerate(flags):
        print(f"{flag} = {settings[index]}")
    print(f"==========================\n")  

    items = Movie.objects.all().order_by('?')[:fetch_movies_count]  # Fetch movies to display on /testdisplay/
    return items


def handle_poster_game(movie_count=1):
    return Movie.objects.all().order_by('?')[:movie_count]  # Fetch the first num_movie
