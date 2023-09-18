from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200, default='NULL')
    release_year = models.IntegerField()
    # runtime = models.IntegerField()
    # imdb_rating = models.IntegerField()
    # mpa_rating = models.CharField(max_length=200)
    # description = models.TextField()
    # tagline = models.TextField()
    # where_to_watch = models.CharField(max_length=200)
    
    def __str__(self):
        underscore_title = self.title.replace(" ", "_")
        return f"{underscore_title}_{self.release_year}"