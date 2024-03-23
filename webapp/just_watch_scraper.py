import requests
from bs4 import BeautifulSoup
import time
import random
from webapp.models import Movie

PROVIDER_LIST = ["Tubi TV", "Pluto TV", "Freevee"]

def generate_movie_justwatch_url(movie):
    slug = movie.title.lower().replace(" ", "-").replace(":", "").replace("&", "and")
    return f"https://www.justwatch.com/us/movie/{slug}"
    
def generate_search_justwatch_url(movie):
    formatted_title = '+'.join(movie.title.split())
    return f"https://www.justwatch.com/us/search?q={formatted_title}"

def fetch_search_justwatch(response, movie):
    try:
        # Check if the response is successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find all title rows
            title_rows = soup.find_all("div", class_="title-list-row__row")
            # Loop through title rows to find matching movie
            for row in title_rows:
                # Extract title
                title_element = row.find("span", class_="header-title")
                if title_element:
                    title = title_element.text.strip()
                    # Check if the title matches the movie we're looking for
                    if title == movie.title:
                        # Extract the URL from the anchor tag within the row
                        anchor_tag = row.find("a")
                        if anchor_tag and "href" in anchor_tag.attrs:
                            url = anchor_tag["href"]
                            return f"https://www.justwatch.com{url}"
            return None
        elif response.status_code == 429:
            return 429
        else:
            print(f"Failed JustWatch scrape for {movie.title} : status code {response.status_code}")
            return None
    except Exception as e:
        print(f"JW search: An error occurred: {e}")
        return None


def parse_movie_page(movie, soup, jw_url_movie):
    title_block = soup.find("div", class_="title-block")
    
    if title_block:
        release_year_element = title_block.find("span", class_="text-muted")
        if release_year_element:
            release_year_text = release_year_element.text.strip()
            release_year = int(release_year_text.strip("()"))
            if movie.release_year == release_year:
                # Find all streaming offers
                streaming_offers = soup.find_all("div", class_="buybox-row stream")
                found_providers = []

                for offer in streaming_offers:
                    # Find streaming providers within the offer
                    offer_providers = offer.find_all("a", class_="offer")
                    for provider in offer_providers:
                        # Extract provider name
                        provider_name = provider.find("img")["alt"]
                        if provider_name in PROVIDER_LIST:
                            # Add the provider to the list of found providers
                            found_providers.append(provider_name)
                # Update the JustWatch URL of the movie in the database
                movie.justwatch_url = jw_url_movie
                movie.save()
                # Return the list of found providers and indicate success
                successful = True
                return found_providers, successful
            else:
                print(f"Release year mismatch for {movie.title}: Database ({movie.release_year}), JustWatch ({release_year})")
        else:
            print(f"Release year not found for {movie.title} on JustWatch.")
    else:
        print(f"Title block not found for {movie.title} on JustWatch.")
    # Return None if parsing fails
    return None


def fetch_search_loop(movie, jw_url_search):
    sleep_add = 0
    jw_url_movie = None    
    while True:
        time.sleep(random.uniform(0, 4))
        response = requests.get(jw_url_search)
        if response.status_code == 200:
            jw_url_movie = fetch_search_justwatch(response, movie)
            return jw_url_movie
        elif response.status_code == 429:
            sleep_time = sleep_add + 10
            sleep_add += 5
            print(f"Received 429 status code for search request. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        else:
            print(f"Failed JustWatch scrape for {movie.title} (search request): status code {response.status_code}")
            return jw_url_movie


def fetch_movie_loop(movie, jw_url_movie):
    sleep_add = 0
    while True:
        time.sleep(random.uniform(0, 4))
        response = requests.get(jw_url_movie)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return parse_movie_page(movie, soup, jw_url_movie)
        elif response.status_code == 429:
            sleep_time = sleep_add + 10
            sleep_add += 5
            print(f"Received 429 status code for movie request. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        else:
            print(f"Failed JW scrape for {movie.title} (movie request): status code {response.status_code}")
            return


def fetch_justwatch(movie, count=0):
    try:     
        jw_url_movie = movie.justwatch_url
        if not jw_url_movie and count == 0:      
            jw_url_search = generate_search_justwatch_url(movie)
            jw_url_movie = fetch_search_loop(movie, jw_url_search)
        if not jw_url_movie:
            jw_url_movie = generate_movie_justwatch_url(movie)
            if count == 1:
                jw_url_movie = f"{jw_url_movie}-{movie.release_year}"
        if jw_url_movie:
            if jw_url_movie == "Not Found":
                return
            count += 1
            found_providers, successful = fetch_movie_loop(movie, jw_url_movie)
            if successful:
                return found_providers
            if count <= 1:
                return found_providers or fetch_justwatch(movie, count=1)
    except Exception as e:
        print(f"An error occurred: {e}")
    return []


def fetch_justwatch(movie, count=0):
    try:
        jw_url_movie = movie.justwatch_url
        
        # If JustWatch URL is not available and it's the first attempt
        if not jw_url_movie and count == 0:      
            # Generate JustWatch search URL for the movie
            jw_url_search = generate_search_justwatch_url(movie)
            # Fetch JustWatch URL through search
            jw_url_movie = fetch_search_loop(movie, jw_url_search)
        
        # If JustWatch URL is still not available
        if not jw_url_movie:
            # Generate JustWatch movie URL for the movie
            jw_url_movie = generate_movie_justwatch_url(movie)
            # Append release year if it's the second attempt
            if count == 1:
                jw_url_movie = f"{jw_url_movie}-{movie.release_year}"
        
        if jw_url_movie:
            count += 1
            # If the movie is not found on JustWatch
            if jw_url_movie == "Not Found":
                return
            
            # Fetch streaming providers
            found_providers, successful = fetch_movie_loop(movie, jw_url_movie)
            # If fetching is successful, return the list of providers
            if successful:
                return found_providers
            # Perform recursive call only if count is less than or equal to 1
            if count <= 1:
                return found_providers or fetch_justwatch(movie, count=1)
    except Exception as e:
        print(f"An error occurred: {e}")
    return []