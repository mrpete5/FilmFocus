import requests
from bs4 import BeautifulSoup
import json
import time
import random

PROVIDER_LIST = ["Tubi TV", "Pluto TV", "Freevee"]

JW_WEB_SCRAPER_URLS_PATH = 'webapp/data/jw_web_scraper_urls.json'


def generate_movie_justwatch_url(movie):
    # Convert the movie title to lowercase
    slug = movie.title.lower()
    # Replace spaces, colons, ampersands
    slug = slug.replace(" ", "-").replace(":", "").replace("&", "and")
    # Remove special characters
    slug = ''.join(char for char in slug if char.isalnum() or char == '-')
    return f"https://www.justwatch.com/us/movie/{slug}"
    
def generate_search_justwatch_url(movie):
    title = movie.title
    formatted_title = '+'.join(title.split())
    return f"https://www.justwatch.com/us/search?q={formatted_title}"

def add_entry_to_json(movie, jw_urls_data):
    new_entry = {'tmdb_id': movie.tmdb_id, 'title': movie.title, 'jw_url': None}
    jw_urls_data.append(new_entry)

    # Update the JSON file with the modified data
    with open(JW_WEB_SCRAPER_URLS_PATH, 'w') as json_file:
        json.dump(jw_urls_data, json_file, indent=4)

def fetch_search_justwatch(response, movie):
    try:
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
                            # Return the formatted URL string
                            return f"https://www.justwatch.com{url}"
            
            # If the movie is not found in any of the title rows
            return None
        elif response.status_code == 429:
            return 429
        else:
            # If the response status code is not 200, print a message indicating failure
            print(f"Failed JustWatch scrape for {movie.title} : status code {response.status_code}")
            return None
    except Exception as e:
        # Print the exception if an error occurs during the execution of the function
        print(f"JW search: An error occurred: {e}")
        return None


def parse_movie_page(movie, soup, jw_url_movie, jw_urls_data):
    # Find the "title-block" div
    title_block = soup.find("div", class_="title-block")

    # If "title-block" div is found, extract the release year
    if title_block:
        release_year_element = title_block.find("span", class_="text-muted")
        if release_year_element:
            release_year_text = release_year_element.text.strip()
            # Extract the release year from the text
            release_year = release_year_text.strip("()")
            # Convert release year to integer
            release_year = int(release_year)

            # Compare the release year with the known release year from your database
            if movie.release_year == release_year:
                # Find all streaming offers
                streaming_offers = soup.find_all("div", class_="buybox-row stream")

                # List to keep track of found providers
                found_providers = []

                # Loop through each streaming offer
                for offer in streaming_offers:
                    # Find streaming providers within the offer
                    offer_providers = offer.find_all("a", class_="offer")
                    for provider in offer_providers:
                        provider_name = provider.find("img")["alt"]
                        if provider_name in PROVIDER_LIST:
                            # Add the provider to the list of found providers
                            found_providers.append(provider_name)

                # Update the JW URL data with the jw_url attribute
                for jw_data in jw_urls_data:
                    if movie.tmdb_id == jw_data.get('tmdb_id'):
                        # Update jw_url if it's None in the JSON data
                        if jw_data.get('jw_url') is None:
                            jw_data['jw_url'] = jw_url_movie
                            # Update the JSON file with the modified data
                            with open(JW_WEB_SCRAPER_URLS_PATH, 'w') as json_file:
                                json.dump(jw_urls_data, json_file, indent=4)
                        break
                # Return the list of found providers
                successful = True
                return found_providers, successful

            else:
                print(f"Release year mismatch for {movie.title}: Database ({movie.release_year}), JustWatch ({release_year})")
        else:
            print(f"Release year not found for {movie.title} on JustWatch.")
    else:
        print(f"Title block not found for {movie.title} on JustWatch.")

    return None


def fetch_search_loop(movie, jw_url_search):
    sleep_add = 0
    jw_url_movie = None    
    while True:
        time.sleep(random.uniform(0, 4))
        response = requests.get(jw_url_search)  # Fetch the search request

        if response.status_code == 200:
            jw_url_movie = fetch_search_justwatch(response, movie)
            return jw_url_movie
        elif response.status_code == 429:
            sleep_time = sleep_add + 10
            sleep_add += 5  # increase by 5 for next time
            print(f"Received 429 status code for search request. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        else:
            print(f"Failed JustWatch scrape for {movie.title} (search request): status code {response.status_code}")
            return jw_url_movie
    

def fetch_movie_loop(movie, jw_url_movie, count, jw_urls_data):
    sleep_add = 0
    while True:
        time.sleep(random.uniform(0, 4))
        response = requests.get(jw_url_movie)

        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')
            return parse_movie_page(movie, soup, jw_url_movie, jw_urls_data)
        elif response.status_code == 429:
            sleep_time = sleep_add + 10
            sleep_add += 5  # increase by 5 for next time
            print(f"Received 429 status code for movie request. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        else:
            if count == 1:
                attempt = "1st attempt"
            else:
                attempt = "2nd attempt"
            print(f"Failed JW scrape {attempt } for {movie.title} (movie request): status code {response.status_code}")
            return


def fetch_justwatch(movie, count=0):
    try:     
        jw_url_movie = None
        found_in_json = False

        # Load the JSON data
        with open(JW_WEB_SCRAPER_URLS_PATH, 'r') as json_file:
                jw_urls_data = json.load(json_file)

        # Check if the movie is already in the JSON data
        for jw_data in jw_urls_data:
            if movie.tmdb_id == jw_data.get('tmdb_id'):
                jw_url_movie = jw_data.get('jw_url')
                found_in_json = True
                break
        
        # If the movie is not found in the JSON data, add it initially
        if not found_in_json:
            add_entry_to_json(movie, jw_urls_data)

            # Load the JSON data again to get the updated data
            with open(JW_WEB_SCRAPER_URLS_PATH, 'r') as json_file:
                jw_urls_data = json.load(json_file)
        
        if not jw_url_movie and count == 0:      
            jw_url_search = generate_search_justwatch_url(movie)
            jw_url_movie = fetch_search_loop(movie, jw_url_search)

        if not jw_url_movie:
            jw_url_movie = generate_movie_justwatch_url(movie)
            if count == 1:
                jw_url_movie = f"{jw_url_movie}-{movie.release_year}"

        if jw_url_movie:
            # Some movies cannot be found on JustWatch
            if jw_url_movie == "Not Found":
                return
            
            count += 1
            found_providers, successful = fetch_movie_loop(movie, jw_url_movie, count, jw_urls_data)

            if successful:
                return found_providers
            # Perform the recursive call only if count is less than or equal to 1
            if count <= 1:
                return found_providers or fetch_justwatch(movie, jw_urls_data, count=1)

    except Exception as e:
        # If any exception occurs during the process, print the error message
        print(f"An error occurred: {e}")

    return []
