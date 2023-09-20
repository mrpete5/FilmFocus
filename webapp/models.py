from django.db import models

# Create your models here.
class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, null=True)
    title = models.CharField(max_length=255)
    overview = models.TextField(null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)
    genres = models.ManyToManyField('Genre', blank=True)
    trailer_key = models.CharField(max_length=255, null=True, blank=True)
    imdb_rating = models.CharField(max_length=10, null=True, blank=True)
    rotten_tomatoes_rating = models.CharField(max_length=10, null=True, blank=True)
    metacritic_rating = models.CharField(max_length=10, null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    domestic_box_office = models.CharField(max_length=100, null=True, blank=True)
    now_playing = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    # mpa_rating = models.CharField(max_length=200)
    # where_to_watch = models.CharField(max_length=200)


    def __str__(self):
        return f"{self.title.replace(' ', '_')}_{self.release_year}"


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
  
