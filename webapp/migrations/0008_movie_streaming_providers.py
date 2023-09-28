# Generated by Django 4.2.5 on 2023-09-27 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0007_streamingprovider'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='streaming_providers',
            field=models.ManyToManyField(blank=True, related_name='movies', to='webapp.streamingprovider'),
        ),
    ]
