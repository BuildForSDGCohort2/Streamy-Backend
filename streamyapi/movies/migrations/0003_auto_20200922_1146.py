# Generated by Django 3.1 on 2020-09-22 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_movie_posted_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='image',
            new_name='poster',
        ),
    ]