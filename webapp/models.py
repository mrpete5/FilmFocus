"""
Name of code artifact: models.py
Brief description: Contains Django ORM models for the FilmFocus web application, defining the structure of the movie and genre database tables.
Programmer’s name: Mark
Date the code was created: 09/17/2023
Dates the code was revised: 10/08/2023
Brief description of each revision & author: Initialized Movie and Genre models (Mark)
Preconditions: Django environment must be set up correctly. The Django ORM must be available and correctly configured.
Acceptable and unacceptable input values or types: Model fields have specific types and constraints as defined in their respective comments.
Postconditions: Provides a representation of the database tables in Python, allowing for database operations via the Django ORM.
Return values or types: Instances of the models represent rows in the database tables.
Error and exception condition values or types that can occur: Errors can occur if there are issues with database operations or if model constraints are violated.
Side effects: Operations on model instances can modify the database.
Invariants: None.
Any known faults: None.
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.db.models import Q
from django.utils.module_loading import import_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
import time
import datetime

class Movie(models.Model):
    """Model representing individual movies in the database."""
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    tmdb_id = models.IntegerField(unique=True, null=True, db_index=True)
    imdb_id = models.CharField(max_length=20, unique=False, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)
    genres = models.ManyToManyField('Genre', blank=True, related_name='movies')
    trailer_key = models.CharField(max_length=255, null=True, blank=True)
    imdb_rating = models.CharField(max_length=10, null=True, blank=True)        # A string with the IMDb rating ("7.4/10"), original API form, use for displaying rating out of 10
    imdb_rating_num = models.FloatField(null=True, blank=True)                  # A float with the IMDb rating (7.4), use this for filtering by IMDb rating
    tmdb_popularity = models.CharField(max_length=10, null=True, blank=True)
    rotten_tomatoes_rating = models.CharField(max_length=10, null=True, blank=True)
    metacritic_rating = models.CharField(max_length=10, null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    domestic_box_office = models.CharField(max_length=100, null=True, blank=True)
    now_playing = models.BooleanField(default=False)
    mpa_rating = models.CharField(max_length=20, null=True, blank=True)
    streaming_providers = models.ManyToManyField('StreamingProvider', blank=True, related_name='movies')
    top_streaming_providers = models.ManyToManyField('StreamingProvider', blank=True, related_name='top_movies')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    recommended_movie_data = models.JSONField(default=list, blank=True)
    letterboxd_rating = models.FloatField(null=True, blank=True)
    # letterboxd_histogram_weights = JSONField(null=True, blank=True) # TODO: Add histogram weights or remove this line

    # String variables for hover over item instructions
    str_addToWatchlist = str("Add Movie to Your Watchlists")
    str_refreshMovieData = str("Retrieve the Newest Movie Data")

    # Movie release date in a printable format
    # To run this code, use "{{ movie.formatted_release_date }}" to execute the printable release date
    release_date = models.DateField(null=True, blank=True)
    def formatted_release_date(self):
        if self.release_date:
            return self.release_date.strftime("%B %d, %Y")  # Example format: "August 8, 2023"
        else:
            return "Unknown"
        
    # readable_form_runtime = models.CharField(max_length=50)
    @property
    def readable_form_runtime(self):
        if self.runtime is None:
            return None
        hours = self.runtime // 60
        minutes = self.runtime % 60
        if hours > 0 and minutes > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} and {minutes} minute{'s' if minutes > 1 else ''}"
        elif hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes > 1 else ''}"

    # This method can be used to generate a unique slug for a movie
    def get_absolute_url(self):
        return reverse('movie_detail', args=[str(self.slug)])
    
    # This method can be used to fetch the recommended movies for a particular movie
    def get_recommended_movies(self, num_movies=6):
        # Dynamically import the process_movie_search function
        process_movie_search = import_string('webapp.services.process_movie_search')
        
        recommended_movies = []
        processed_movies = set()  # Keep track of processed movies to avoid duplicates
        fetches_per_second = 20  # Updated to 20 requests per second as per requirement

        # Semaphore to limit the number of concurrent API fetches
        semaphore = Semaphore(fetches_per_second)

        def fetch_and_process_movie(movie_data):
            tmdb_id = movie_data.get('tmdb_id')
            title = movie_data.get('title')
            if tmdb_id not in processed_movies:
                with semaphore:
                    # Ensure we don't make more than 10 requests per second
                    time.sleep(1/fetches_per_second)
                    process_movie_search(tmdb_id, title)
                    processed_movies.add(tmdb_id)

        # Use a thread pool to process movies in parallel
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_and_process_movie, movie_data) for movie_data in self.recommended_movie_data]
            for future in as_completed(futures):
                try:
                    # If the function returns a result, it will be available as future.result()
                    result = future.result()
                except Exception as e:
                    # Handle exception
                    print(f"An error occurred: {str(e)}")

        # Fetch recommended movies from the database
        for movie_data in self.recommended_movie_data:
            tmdb_id = movie_data.get('tmdb_id')
            recommended_movie = Movie.objects.filter(tmdb_id=tmdb_id).first()
            if recommended_movie:
                recommended_movies.append(recommended_movie)

        # If the number of recommended movies is less than the desired number,
        # add the most recently added movies from the existing database.
        if len(recommended_movies) < num_movies:
            # Get the genres of the original movie
            original_movie_genres = self.genres.all()
            
            # Fetch additional movies that share at least one genre with the original movie
            # and are not already in the recommended_movies list.
            additional_movies = Movie.objects.exclude(pk__in=[movie.pk for movie in recommended_movies])\
                .filter(genres__in=original_movie_genres)\
                .distinct()\
                .order_by('-created_at')[:num_movies - len(recommended_movies)]
            
            recommended_movies.extend(additional_movies)
        
        # Return the specified number of recommended movies
        return recommended_movies[:num_movies]


    def save(self, *args, **kwargs):
        self.slug = self.get_slug()
        super().save(*args, **kwargs)

    # Converts a normal string into a URL slug
    def get_slug(self):
        base_slug = f"{slugify(self.title)}-{self.release_year}"
        slug = base_slug
        # Exclude the current Movie object from the exists check
        existing_movies = Movie.objects.filter(slug=slug).exclude(pk=self.pk)
        # Use a loop to handle the rare case where multiple existing movies have the same base slug
        counter = 2  # Start counter at 2
        while existing_movies.exists():
            slug = f"{base_slug}-{counter}"
            existing_movies = Movie.objects.filter(slug=slug).exclude(pk=self.pk)
            counter += 1
        return slug

    # String representation of the Movie model
    def __str__(self):
        return f"{self.title.replace(' ', '_')}_{self.release_year}"


class Genre(models.Model):
    """Model representing movie genres in the database."""
    name = models.CharField(max_length=100)

    # String representation of the Genre model
    def __str__(self):
        return self.name


class StreamingProvider(models.Model):
    """Model representing streaming providers in the database."""
    name = models.CharField(max_length=255)
    logo_path = models.CharField(max_length=255, null=True, blank=True)
    provider_id = models.IntegerField(unique=True)
    ranking = models.IntegerField(default=1000)  # Lower numbers indicate higher preference

    def __str__(self):
        return self.name
    

class UserProfile(models.Model):
    """Model representing user profiles with additional information and friend relationships."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # links to built-in Django User model
    friends = models.ManyToManyField('self', blank=True)
    biography = models.CharField(max_length=300, blank=True)
    PROFILE_PICS_CHOICES = [
        ('default.png', 'Default'),
        ('man_suit.png', 'Man in Suit'),
        ('man_hoodie.png', 'Man in Hoodie'),
        ('woman_glasses.png', 'Woman with Glasses'),
        ('woman_suit.png', 'Woman in Suit'),
        ('girl_bow.png', 'Girl with Bow'),
        ('boy_smile.png', 'Boy with Smile'),
        ('man_beard.png', 'Man with Beard'),
    ]
    profile_pic = models.CharField(max_length=100, choices=PROFILE_PICS_CHOICES, default='default.jpg')
    
    def __str__(self):
        return f"{self.user.username}"
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    watchlist_name = models.CharField(max_length=100)
    is_private = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s {self.watchlist_name} Watchlist"
    

class WatchlistEntry(models.Model):
    ''' Model representing an entry in a user's watchlist. '''
        
    watchlist = models.ForeignKey(Watchlist, related_name='entries', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('watchlist', 'movie')  # Each movie can only appear once in each watchlist

    def __str__(self):
        return f"{self.movie.title} in {self.watchlist.watchlist_name}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(UserProfile, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, related_name='to_user', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('to_user', 'from_user')

    def __str__(self):
        return f"{self.from_user.user.username}'s request to {self.to_user.user.username}"
