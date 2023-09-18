from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index2/", views.index2, name="index2"),
    path("details1/", views.details1, name="details1"),
    path("details2/", views.details2, name="details2"),
    path("catalog1/", views.catalog1, name="catalog1"),
    path("catalog2/", views.catalog2, name="catalog2"),
    path("about/", views.about, name="about"),
    path("404/", views.four04, name="404"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("faq/", views.faq, name="faq"),
    path("movies/", views.movies, name="movies"),
]
