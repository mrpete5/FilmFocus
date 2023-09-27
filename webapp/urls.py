"""
Name of code artifact: urls.py
Brief description: Contains URL patterns for the FilmFocus web application, mapping URLs to their respective view functions.
Programmer’s name: Mark
Date the code was created: 09/17/2023
Dates the code was revised: 09/21/2023
Brief description of each revision & author: Initialized URL patterns for various pages (Mark)
Preconditions: Django environment must be set up correctly. The views module must be available and correctly set up.
Acceptable and unacceptable input values or types: None. This module defines URL patterns.
Postconditions: Provides a mapping of URLs to view functions.
Return values or types: None. This module is used by Django to determine which view function to call for a given URL.
Error and exception condition values or types that can occur: Errors can occur if there's a mismatch between a URL pattern and its associated view function.
Side effects: None.
Invariants: None.
Any known faults: None.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('movie/<slug:movie_slug>/', views.movie_detail, name='movie_detail'),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("about/", views.about, name="about"),
    path("404/", views.four04, name="404"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("faq/", views.faq, name="faq"),
    path("testdisplay/", views.testdisplay, name="testdisplay"),
    path("testforban/", views.testforban, name="testforban"),
]
