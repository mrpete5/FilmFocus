## Add Movie to Watchlist Documentation

## Overview
The Add Movie to Watchlist functionality works with the watchlist popups and the Django databases (models).
User clicks the add button on a movie poster and sees the watchlist popup. Then they select the watchlist they want
to add the movie to and click the add button. Then the selected movie is added to the apoplicable watchlist databases.

## Implementation Details
Here is an explanation of how clicking the "Add to Watchlist" button creates a new watchlist entry:

1. The button has two data attributes - data-movie-id and data-watchlist-id. These contain the database IDs for the movie and watchlist.

2. When the button is clicked, a JavaScript click handler is triggered. 

3. The click handler retrieves the two IDs from the data attributes using:

main.js
```js
const movieId = button.dataset.movieId;
const watchlistId = button.dataset.watchlistId; 
```

4. An AJAX POST request is made to the backend add_to_watchlist view, passing the two IDs in the request body. 

5. The view gets the Movie and Watchlist objects corresponding to those IDs:

view.py
functions( TODO: TBD *****)
```python
movie = Movie.objects.get(id=movie_id)
watchlist = Watchlist.objects.get(id=watchlist_id)
```

6. It then creates a new WatchlistEntry object to associate that movie with the watchlist:

view.py
```python 
WatchlistEntry.objects.create(
  watchlist=watchlist, 
  movie=movie
)
```

7. This creates and saves the new watchlist entry in the database. 

8. The view returns a success response that is handled by the frontend.

9. The frontend can then update the UI to show the movie was added.

So in summary, the button click handler makes a request passing IDs, the view looks up objects and creates the entry, and the frontend handles the response.
