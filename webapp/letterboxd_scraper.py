# Scrape.py
# Decsription: Scrapes letterboxd.com for Rating Information
#
# Author: John Zheng

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import csv

                                                # CAUTION: Caching to reduce traffic on letterboxd during testing/development
do_caching = False                              # option whether or not to perform caching
cache_dir = "letterboxd_rating_cache" + "/"     # need the '/' at the end for directory

def saveRating(filepath, rating_info):
    # Write a Cached Version of rating_info
    with open(filepath, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in rating_info.items():
            writer.writerow([key, value])
def loadRating(filepath):
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
    
def getRating(movie_name):
    # Return Cached Version of Rating Info If Already Exist
    if do_caching and os.path.exists(cache_dir+movie_name+".csv"):
        print("Cached Version Found")
        return loadRating(cache_dir+movie_name+".csv")

    # Dictionary of Returned Rating Information
    rating_info = {
        "Histogram Counts" : [],
        "Histogram Weights" : [],
    }

    try:
        # Makes HTTPS Request for HTML
        url = "https://letterboxd.com/csi/film/" + movie_name + "/rating-histogram"
        headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.5;) Gecko/20100101 Firefox/56.7"}
        request = Request(url, headers=headers)
        page = urlopen(request)

        # Convert the Request to a Readable HTML
        html_bytes = page.read()

        # Create BeautifulSoup parser object
        soup = BeautifulSoup(html_bytes, "html.parser")

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


        # Save
        if do_caching:
            saveRating(cache_dir+movie_name+".csv", rating_info)

        # Returns the Rating Information and Notifies it was Scraped
        print("Rating Info Scraped from Letterboxd")
        return rating_info
    except Exception as e:
        print("Failure to Scrape:", str(e))
        return None


def main(rd):
    title_name = rd.lower().replace(" ", "-")
    release_year = "2011"
    
    rating_dict = getRating(title_name+"-"+release_year)
    if not rating_dict:
        rating_dict = getRating(title_name)
    print(rating_dict)
