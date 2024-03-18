import requests
from bs4 import BeautifulSoup

PROVIDER_LIST = ["Tubi TV", "Pluto TV", "Freevee"]

def generate_justwatch_url(movie, call_number):
    # Convert the movie title to lowercase
    slug = movie.title.lower()
    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")
    # Remove special characters
    slug = ''.join(char for char in slug if char.isalnum() or char == '-')
    
    if call_number != 0:
        slug += f"-{movie.release_year}"
    # Construct the full URL
    return f"https://www.justwatch.com/us/movie/{slug}"


def fetch_justwatch(movie, call_number=0):
    try:
        if call_number > 1:
            return
        # Generate the JustWatch URL based on the movie slug
        url = generate_justwatch_url(movie, call_number)

        # Send a GET request to the URL
        response = requests.get(url)

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
                                    # Add the provider to the list of found providers
                                    found_providers.append(provider_name) 

                        # Return the list of found providers
                        return found_providers

                    else:
                        call_number += 1
                        if call_number < 2:
                            return fetch_justwatch(movie, call_number)
                        else:
                            print(f"Release year mismatch for {movie.title}: Database ({movie.release_year}), JustWatch ({release_year})")
                else:
                    print(f"Release year not found for {movie.title} on JustWatch.")
            else:
                print(f"Title block not found for {movie.title} on JustWatch.")
        else:
            # If the response status code is not 200, print a message indicating failure
            # print("Failed JustWatch scrape for", movie.title, "("+str(movie.release_year)+")")
            pass
    except Exception as e:
        # If any exception occurs during the process, print the error message
        print(f"An error occurred: {e}")

    return []
