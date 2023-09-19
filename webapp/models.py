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
    # imdb_rating = models.IntegerField()
    # mpa_rating = models.CharField(max_length=200)
    # where_to_watch = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title.replace(' ', '_')}_{self.release_year}"


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
  
