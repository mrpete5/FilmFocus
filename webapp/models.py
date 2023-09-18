from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200)
    releaseYear = models.IntegerField()
    # runtime = models.IntegerField()
    # imdbRating = models.IntegerField()
    # mpaRating = models.CharField(max_length=200)
    # description = models.TextField()
    # tagline = models.TextField()
    # whereToWatch = models.CharField(max_length=200)
    