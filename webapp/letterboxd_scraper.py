# letterboxd_scraper.py
# Description: Scrapes letterboxd.com for Rating Information
#
# Author: John Zheng

import requests
from bs4 import BeautifulSoup
import os
import csv

                                                # CAUTION: Caching to reduce traffic on letterboxd during testing/development
do_caching = False                              # option whether or not to perform caching
cache_dir = "letterboxd_rating_cache" + "/"     # need the '/' at the end for directory

# Save or load information for caching and cached items
def save_rating(filepath, rating_info):
    # Write a Cached Version of rating_info
    with open(filepath, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in rating_info.items():
            writer.writerow([key, value])
def load_rating(filepath):
    # Read Rating Information to loaded_dict
    loaded_dict = {}
    with open(filepath, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            key, value = row
            loaded_dict[key] = value

    # Caste Weighted Average as a Float
    if "Weighted Average" in loaded_dict:
        loaded_dict["Weighted Average"] = float(loaded_dict["Weighted Average"])

    # Caste Rating 
    if "Histogram Counts" in loaded_dict:
        increment_percents_str = loaded_dict["Histogram Counts"]
        loaded_dict["Histogram Counts"] = [int(x) for x in increment_percents_str.strip('[]').split(',')]

    # Caste Rating 
    if "Histogram Weights" in loaded_dict:
        increment_percents_str = loaded_dict["Histogram Weights"]
        loaded_dict["Histogram Weights"] = [float(x) for x in increment_percents_str.strip('[]').split(',')]

    # Return Rating Info
    return loaded_dict
    
def convert_to_hyphenated_name(input_string):
    # Whitelisted Characters
    whitelist_char = [' ', '-']

    # Delete any character that is not alphanumeric or whitelisted
    hyphenated_string = ''.join(char if char.isalnum() or char in whitelist_char  else '' for char in input_string)
    
    # Replace white space with hyphens
    hyphenated_string = hyphenated_string.replace(' ', '-').replace('\t', '-').replace('\n', '-').replace('\r', '-')

    # Remove consecutive hyphens and leading/trailing hyphens
    hyphenated_string = "-".join(filter(None, hyphenated_string.split("-")))

    # Convert to lowercase
    hyphenated_string = hyphenated_string.lower()

    return hyphenated_string

# Used by get_rating() to request from letterboxd using movie_name
def get_rating_direct(movie_name):
    # Return Cached Version of Rating Info If Already Exist
    if do_caching and os.path.exists(cache_dir+movie_name+".csv"):
        print("Cached Version Found")
        return load_rating(cache_dir+movie_name+".csv")

    # Dictionary of Returned Rating Information
    rating_info = {
        "Histogram Counts" : [],
        "Histogram Weights" : [],
    }

    # Make URL
    url = "https://letterboxd.com/csi/film/" + movie_name + "/rating-histogram"
    
    # Form Request Header
    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.5;) Gecko/20100101 Firefox/56.7"}

    # Attempt to Make Request to Letterboxd 3 Times Before Giving Up
    for i in range(3):
        try:
            response = requests.get(url, headers=headers,timeout=5) # Attempt Request
            response.raise_for_status()                             # Throw Exception When Failed
            break                                                   # Break Loop If No Problems
        except requests.exceptions.Timeout:
            print("Attempt", i+1, "Timeout Reached. Retrying...")   # Notify Timeout
        except Exception as e:
            return None

    # Convert Response to HTML
    html = response.text

    # Create BeautifulSoup parser object
    soup = BeautifulSoup(html, "html.parser")

    # Get histogramed Ratings by Percent
    rating_histogram_elements = soup.find_all(class_="rating-histogram-bar")
    if rating_histogram_elements:
        for element in rating_histogram_elements:
            ir_element = element.find(class_="ir")
            if ir_element:
                rating_histogram_content = ir_element.get("title")
                rating_histogram_split = rating_histogram_content.split()
                rating_info["Histogram Counts"].append(
                    int(rating_histogram_split[0].replace(",", "")))
                rating_info["Histogram Weights"].append(
                    float(rating_histogram_split[3].strip("()").rstrip("%")))
            else:
                rating_info["Histogram Counts"].append(0)
                rating_info["Histogram Weights"].append(0.0)

    # Get Weighted Average
    rating_element = soup.find("a", class_="display-rating")
    if rating_element:
        rating_content = rating_element.get("title")
        rating = float(rating_content.split()[3])
        rating_info["Weighted Average"] = rating
    else:
        rating = 0.0
        for i in range(0, 10):
            current_rating = i * 0.5 + 0.5
            rating += current_rating * (rating_info["Histogram Weights"][i] * 0.01)
        rating_info["Weighted Average"] = rating


    # Save to Cache
    if do_caching:
        save_rating(cache_dir+movie_name+".csv", rating_info)

    # Returns the Rating Information and Notifies it was Scraped
    return rating_info
    
# Returns a dictionary of rating information from a movie name and year
def get_rating(movie_name, year):
    # Convert movie_name to something that makes sense for letterboxd
    title_name = convert_to_hyphenated_name(movie_name)

    # Try to get rating information from url with and without the year appended to movie title
    rating_dict = get_rating_direct(title_name+"-"+str(year))
    if not rating_dict:
        rating_dict = get_rating_direct(title_name)

    return rating_dict
