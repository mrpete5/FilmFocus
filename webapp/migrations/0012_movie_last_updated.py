# Generated by Django 4.2.5 on 2023-12-17 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0011_movie_imdb_rating_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
