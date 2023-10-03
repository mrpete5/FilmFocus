==================== Help with our APIs ====================

- APIs used:
    - The Movie Database (TMDb)
        - https://developer.themoviedb.org/reference/intro/getting-started
    - The Open Movie Database (OMDb)
        - https://www.omdbapi.com/


- TMDb:
    - Types of calls:
        - Now Playing: Gets pages of 20 movies each. Minimal movie data within. Used for new releases.
            - Called with fetch_now_playing_movies(start_page, end_page)

        - Popular: Gets pages of 20 movies. Minimal movie data within. Used for the majority of our database.
            - Called with fetch_popular_movies(start_page, end_page)

        - Details: Gets data for 1 movie. Used in conjunction with other calls to get the majority of our movie data.
            - Called with fetch_movie_details_from_tmdb(tmdb_id)

        - Appended to the Details call:
            - Videos: Gets links to movie trailers.
            - Watch Providers: Gets the movie streaming providers.
            - Recommendations: Gets the TMDB recommendations for a movie.
            - Similar: Gets the TMDB similar movies for a movie. Added with the recommendations.


- OMDb:
    - Called with fetch_movie_data_from_omdb(imdb_id) in process_movie_search()
    - Used to get:  
        - imdb_rating
        - rotten_tomatoes_rating
        - metacritic_rating
        - director
        - domestic_box_office
        - mpa_rating