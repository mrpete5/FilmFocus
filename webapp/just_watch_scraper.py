import requests
from bs4 import BeautifulSoup
import json
import time
import random

PROVIDER_LIST = ["Tubi TV", "Pluto TV", "Freevee"]

# Read JW URL data from the JSON file
JW_WEB_SCRAPER_URLS_PATH = 'webapp/data/jw_web_scraper_urls.json'
with open(JW_WEB_SCRAPER_URLS_PATH, 'r') as json_file:
    jw_urls_data = json.load(json_file)


def generate_justwatch_url(movie, call_number):
    # Convert the movie title to lowercase
    slug = movie.title.lower()
    # Replace spaces, colons, ampersands
    slug = slug.replace(" ", "-").replace(":", "").replace("&", "and")
    # Remove special characters
    slug = ''.join(char for char in slug if char.isalnum() or char == '-')
    
    if call_number != 0:
        slug += f"-{movie.release_year}"
    # Construct the full URL
    return f"https://www.justwatch.com/us/movie/{slug}"


def fetch_justwatch(movie, jw_urls_data, call_number=0, sleep_add=0):
    try:
        if call_number > 1:
            return
        # Use jw_urls_data to get the JW URL for the movie
        jw_url = None
        found_in_json = False
        for jw_data in jw_urls_data:
            if movie.tmdb_id == jw_data.get('tmdb_id'):
                jw_url = jw_data.get('jw_url')
                found_in_json = True
                break
        
        if not jw_url:
            # JW URL not found, generate it
            jw_url = generate_justwatch_url(movie, call_number)
            # Add the JW URL data to jw_urls_data if count is 0 and movie's tmdb_id is not found in JSON
            if call_number == 0 and not found_in_json:
                new_entry = {'tmdb_id': movie.tmdb_id, 'title': movie.title, 'jw_url': None}
                jw_urls_data.append(new_entry)

                # Update the JSON file with the modified data
                with open(JW_WEB_SCRAPER_URLS_PATH, 'w') as json_file:
                    json.dump(jw_urls_data, json_file, indent=4)

        time.sleep(random.uniform(0, 7))  # Random sleep between 0 and 7 seconds to avoid overloading server
        # time.sleep(2)
        # Send a GET request to the URL
        response = requests.get(jw_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

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
                                    # print(f"Found provider {provider_name} for {movie.title} {movie.release_year}")   # TODO, for testing
                                    # Add the provider to the list of found providers
                                    found_providers.append(provider_name) 

                        # Update the JW URL data with the jw_url attribute
                        for jw_data in jw_urls_data:
                            if movie.tmdb_id == jw_data.get('tmdb_id'):
                                # Update jw_url if it's None in the JSON data
                                if jw_data.get('jw_url') is None:
                                    jw_data['jw_url'] = jw_url
                                    # Update the JSON file with the modified data
                                    with open(JW_WEB_SCRAPER_URLS_PATH, 'w') as json_file:
                                        json.dump(jw_urls_data, json_file, indent=4)
                                
                                # print("Successfully updated jw_url for", movie.title, "("+str(movie.release_year)+")") # TODO, for testing
                                break

                        # Return the list of found providers
                        return found_providers

                    else:
                        call_number += 1
                        if call_number < 2:
                            return fetch_justwatch(movie, jw_urls_data, call_number)
                        else:
                            print(f"Release year mismatch for {movie.title}: Database ({movie.release_year}), JustWatch ({release_year})")
                else:
                    print(f"Release year not found for {movie.title} on JustWatch.")
            else:
                print(f"Title block not found for {movie.title} on JustWatch.")
        
        elif response.status_code == 429:
            sleep_time = sleep_add + 10
            sleep_add += 5  # increase by 5 for next time
            print(f"Received 429 status code. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
            return fetch_justwatch(movie, jw_urls_data, call_number, sleep_add)
        else:
            # If the response status code is not 200, print a message indicating failure
            print(f"Failed JustWatch scrape for {movie.title} ({movie.release_year}) : status code {response.status_code}") # TODO, for testing
            # pass
    except Exception as e:
        # If any exception occurs during the process, print the error message
        print(f"An error occurred: {e}")

    return []
