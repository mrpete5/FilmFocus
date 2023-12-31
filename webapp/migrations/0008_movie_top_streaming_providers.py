# Generated by Django 4.2.5 on 2023-12-02 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0007_alter_userprofile_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='top_streaming_providers',
            field=models.ManyToManyField(blank=True, related_name='top_movies', to='webapp.streamingprovider'),
        ),
    ]
