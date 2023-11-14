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
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Pay attention to the different naming schemes
    path("", views.index, name="index"),
    path('movie/<slug:movie_slug>/', views.movie_detail, name='movie_detail'),
    path('add_to_watchlist/<int:watchlist_id>/<int:movie_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('create_watchlist/<str:watchlist_name>', views.create_watchlist, name='create_watchlist'),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("about/", views.about, name="about"),
    path("404/", views.four04, name="404"),
    path("pwreset/", views.pwreset, name="pwreset"),                                        # Page for requesting a password reset
    path("reset/<uidb64>/<token>/", views.pwresetconfirm, name="password_reset_confirm"),   # Page that processes the password reset
    path("password_reset_sent/", auth_views.PasswordResetDoneView.as_view(),                # Page that tells user pass reset email is sent
          name="password_reset_done"),
    path("password_reset/", auth_views.PasswordResetView.as_view(),                         # Django's default page for requesting a password reset (uses email instead)
          name="password_reset"),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(),        # Page that comfirms the password has been changed
          name="password_reset_complete"),
    path("login/", views.login_user, name="login"),         # Leave the different naming schemes as is
    path("logout/", views.logout_user, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("faq/", views.faq, name="faq"),
    path("testdisplay/", views.testdisplay, name="testdisplay"),
    path("testforban/", views.testforban, name="testforban"),
    path("search/", views.searchBar, name="search"),
    path("searchbar/<str:query>", views.searchbar, name="searchbar"),
    path("popup/<int:movie_id>", views.popup, name="popup"),
]
