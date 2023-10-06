# LetterBoxd Scraper Documentation

## Overview
The `letterboxd.py` script provides a set of functions for web scraping data from Letterboxd. It retrieves rating information from Letterboxd.com based on the name of a movie as a string and its release year. The script returns a dictionary containing the following:

- A list of the number of reviews for each rating increment in the rating histogram.
- A list of the weights of each rating increment in the rating histogram.
- The weighted average rating as a floating-point number.

## Usage

To use `letterboxd_scraper.py`, follow these steps:

1. Import the script into your Python file:
    ```python
    import webapp.letterboxd_scraper as lbd_scrape
    ```

2. Get the rating information dictionary from Letterboxd by providing the movie's name and release year:
    ```python
    rating_dict = lbd_scrape.get_rating("Spider-Man: Into the Spider-Verse", 2018)
    ```
    or if you have a movie object:
    ```python
    rating_dict = lbd_scrape.get_rating(movie.title, movie.release_year)
    ```

3. Extract the weighted average rating as a floating-point number from the rating dictionary:
    ```python
    rating_average = rating_dict["Weighted Average"]
    ```

4. Retrieve the histogram weights from the rating dictionary:
    ```python
    rating_histogram = rating_dict["Histogram Weights"]
    ```

5. Obtain the histogram review counts from the rating dictionary:
    ```python
    rating_histogram_counts = rating_dict["Histogram Counts"]
    ```

That's how you can use the LetterBoxd scraper script to fetch and work with movie rating information.
