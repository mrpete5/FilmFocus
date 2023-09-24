"""
Name of code artifact: models.py
Brief description: Contains Django ORM models for the FilmFocus web application, defining the structure of the movie and genre database tables.
Programmer’s name: Mark
Date the code was created: 09/17/2023
Dates the code was revised: 09/21/2023
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

from django.db import models

# Movie model representing individual movies in the database
class Movie(models.Model):
    # Fields for the Movie model with their respective constraints
    entry_id = models.AutoField(primary_key=True) # number of entry as saved into database
    title = models.CharField(max_length=255)
    tmdb_id = models.IntegerField(unique=True, null=True)
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
    # where_to_watch = models.CharField(max_length=200)

    # String representation of the Movie model
    def __str__(self):
        return f"{self.title.replace(' ', '_')}_{self.release_year}"

# Genre model representing movie genres in the database
class Genre(models.Model):
    # Field for the Genre model
    name = models.CharField(max_length=100)

    # String representation of the Genre model
    def __str__(self):
        return self.name
