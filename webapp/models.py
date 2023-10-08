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

import random
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.db.models import Q
from django.utils.module_loading import import_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse



class Movie(models.Model):
    """Model representing individual movies in the database."""
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    tmdb_id = models.IntegerField(unique=True, null=True, db_index=True)
    imdb_id = models.CharField(max_length=20, unique=False, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)
    genres = models.ManyToManyField('Genre', blank=True)
    trailer_key = models.CharField(max_length=255, null=True, blank=True)
    imdb_rating = models.CharField(max_length=10, null=True, blank=True)
    tmdb_popularity = models.CharField(max_length=10, null=True, blank=True)
    rotten_tomatoes_rating = models.CharField(max_length=10, null=True, blank=True)
    metacritic_rating = models.CharField(max_length=10, null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    domestic_box_office = models.CharField(max_length=100, null=True, blank=True)
    now_playing = models.BooleanField(default=False)
    mpa_rating = models.CharField(max_length=20, null=True, blank=True)
    streaming_providers = models.ManyToManyField('StreamingProvider', blank=True, related_name='movies')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    recommended_movie_data = models.JSONField(default=list, blank=True)
    letterboxd_rating = models.FloatField(null=True, blank=True)
    # letterboxd_histogram_weights = JSONField(null=True, blank=True) # TODO: Add histogram weights or remove this line

    # This method can be used to generate a unique slug for a movie
    def get_absolute_url(self):
        return reverse('movie_detail', args=[str(self.slug)])
    
    # This method can be used to fetch the recommended movies for a particular movie
    def get_recommended_movies(self, num_movies=6):
        # Dynamically import the process_movie_search function
        process_movie_search = import_string('webapp.services.process_movie_search')
        
        recommended_movies = []
        processed_movies = set()  # Keep track of processed movies to avoid duplicates
        
        for movie_data in self.recommended_movie_data:
            if len(recommended_movies) >= num_movies:
                break  # Stop processing when the desired number of movies is reached
            
            tmdb_id = movie_data.get('tmdb_id')
            if tmdb_id in processed_movies:
                continue  # Skip processing if the movie has already been processed
            
            title = movie_data.get('title')
            recommended_movie = Movie.objects.filter(tmdb_id=tmdb_id).first()
            
            if recommended_movie:
                recommended_movies.append(recommended_movie)
                processed_movies.add(tmdb_id)
            else:
                # Fetch and save the recommended movie details if it doesn't exist in your database
                process_movie_search(tmdb_id, title)
                recommended_movie = Movie.objects.filter(tmdb_id=tmdb_id).first()
                
                if recommended_movie:
                    recommended_movies.append(recommended_movie)
                    processed_movies.add(tmdb_id)
        
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

    def __str__(self):
        return self.name
    

class UserProfile(models.Model):
    """Model representing user profiles with additional information and friend relationships."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # links to built-in Django User model
    friends = models.ManyToManyField('self', blank=True)
    

from django.contrib.auth.models import User

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    # user = models.ForeignKey(User, related_name='watchlists', on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)

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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
