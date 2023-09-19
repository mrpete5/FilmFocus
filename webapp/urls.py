from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("details/", views.details, name="details"),
    path("catalog/", views.catalog, name="catalog"),
    path("about/", views.about, name="about"),
    path("404/", views.four04, name="404"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("faq/", views.faq, name="faq"),
    path("movies/", views.movies, name="movies"),
]
