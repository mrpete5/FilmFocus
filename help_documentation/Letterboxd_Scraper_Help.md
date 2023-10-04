### LetterBoxd Scraper Documentation

## Overview:
    - The letterboxd.py script provides a set of functions that are used
    to webscrape letterboxd. It gets the rating information from letterboxd.com
    using the name of a movie as a string and its release year. It returns a 
    dictionary of the list of amount of reviews for each increment of a rating
    histogram, the list of weights of each increment of a rating histogram, 
    and the weighted average as a float.


## Usage:
To use letterboxd_scraper.py:
    - import into a file
        import webapp.letterboxd_scraper as lbd_scrape
    - get the rating information dictionary from letterboxd
        rating_dict = lbd_scrape.get_rating("Spider-Man: Into the Spider-Verse", 2018)
        rating_dict = lbd_scrape.get_rating(movie.title, movie.release_year)
    - get the weighted average float from the rating dictionary
        rating_average = rating_dict["Weighted Average"]
    - get the histogram weights from the rating dictionary
        rating_histogram = rating_dict["Histogram Weights"]
    - get the histogram review counter from the rating dictionary
        rating_histogram = rating_dict["Histogram Counts"]
