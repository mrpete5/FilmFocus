# Generated by Django 4.2.5 on 2023-09-21 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0014_movie_is_popular'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='mpa_rating',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
