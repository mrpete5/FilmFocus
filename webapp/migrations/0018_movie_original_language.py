# Generated by Django 4.2.5 on 2024-03-24 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0017_movie_justwatch_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='original_language',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
