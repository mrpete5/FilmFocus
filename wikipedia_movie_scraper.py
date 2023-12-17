"""
Wikipedia Web Scraper for FilmFocus App (webapp)
wikipedia_movie_scraper.py

Description:
    This script is designed to scrape movie details from Wikipedia pages and save the information into the FilmFocus app's database. It is part of the 'webapp' Django project. The scraper fetches details like title, release year, director, runtime, and other relevant data, and populates them into the 'Movie' model in the database.

Usage:
    Call the `get_wiki_movie_data(movie_name)` function with the movie name to scrape data from Wikipedia. The scraped data is then saved into the database using the `save_movie_to_database` function.

Dependencies:
    - requests: For making HTTP requests.
    - BeautifulSoup: For parsing HTML content.
    - re: For regular expression operations.
    - logging: For logging information and errors.
"""

import requests
from bs4 import BeautifulSoup
from webapp.models import Movie         #Genre, StreamingProvider  Import from your Django app
from django.utils.text import slugify
import re
import logging
import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')

# Initialize Django
django.setup()

# Set up logging
logger = logging.getLogger(__name__)

def get_wiki_movie_data(movie_name, retry_count=1):
    """
    Fetches movie details from a Wikipedia page.

    Args:
        movie_name (str): The name of the movie to search for.
        retry_count (int): The number of retries for the HTTP request in case of failure.

    Returns:
        dict: A dictionary containing scraped movie data.
    """
    base_url = "https://en.wikipedia.org/wiki/"
    movie_url = base_url + movie_name.replace(' ', '_')  # Format the movie name for URL
    attempt = 0

    while attempt <= retry_count:
        try:
            # Make the HTTP request to Wikipedia
            response = requests.get(movie_url, timeout=5)
            response.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout occurred: {e}")
            attempt += 1
            if attempt > retry_count:
                return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    info_box = soup.find('table', class_='infobox')

    # Extract movie data from the info box
    movie_data = {}
    if info_box:
        for row in info_box.find_all('tr'):
            header = row.find('th')
            if header and header.text:
                key = header.text.strip()
                value = row.find('td')
                if value:
                    movie_data[key] = value.text.strip()

    return movie_data

def save_movie_to_database(movie_data):
    """
    Saves the movie data to the database using the Movie model.

    Args:
        movie_data (dict): The dictionary containing movie data scraped from Wikipedia.
    """
    required_fields = ['Title', 'Release date']  # Essential fields for a movie record
    if not all(field in movie_data for field in required_fields):
        logger.error("Essential movie data is missing. Skipping save.")
        return

    movie = Movie()
    movie.title = movie_data.get('Title', '')

    # Process release year and handle exceptions
    try:
        movie.release_year = int(movie_data.get('Release date', '').split(',')[1].strip())
    except (ValueError, IndexError):
        logger.error("Invalid release year format.")
        movie.release_year = None

    # Additional field mappings and processing as required
    # ...

    movie.save()

def scrape_movies(test_mode=False, limit=0):
    """
    Scrapes Wikipedia for movie details for each movie in the Movie model.
    Args:
        test_mode (bool): Whether to run in test mode.
        limit (int): The maximum number of movies to scrape in test mode.
    """
    if test_mode and limit > 0:
        movies = Movie.objects.all()[:limit]
    else:
        movies = Movie.objects.all()

    success_count = 0
    for movie in movies:
        movie_data = get_wiki_movie_data(movie.title)
        if movie_data and save_movie_to_database(movie, movie_data):
            success_count += 1

    total_movies = len(movies)
    success_rate = (success_count / total_movies) * 100
    print(f"Attempted to scrape {total_movies} movies.")
    print(f"Success rate: {success_rate:.2f}%")

def main():
    # Example usage
    scrape_movies(test_mode=True, limit=10)

if __name__ == "__main__":
    main()