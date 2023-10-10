from django import template

register = template.Library()

@register.filter
def get_movies(watchlist_entries):
    return [entry.movie for entry in watchlist_entries.all()]
