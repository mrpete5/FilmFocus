# Generated by Django 4.2.5 on 2023-09-24 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='entry_id',
            new_name='id',
        ),
    ]