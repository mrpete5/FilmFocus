# Generated by Django 4.2.5 on 2023-12-02 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0009_streamingprovider_ranking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streamingprovider',
            name='ranking',
            field=models.IntegerField(default=1000),
        ),
    ]
