
import os
import sys
import django

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Append the parent directory (FilmFocus) to the system path
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFocus.settings')
django.setup()

from django.contrib.auth.models import User
from webapp.models import Watchlist, WatchlistEntry, Movie

def list_users():
    users = User.objects.all()
    for user in users:
        print(user.id, user.username)

def select_user():
    user_id = input("Enter the ID of the user whose watchlist you want to copy: ")
    try:
        user = User.objects.get(id=user_id)
        return user
    except User.DoesNotExist:
        print("User does not exist.")
        return None

def list_watchlists(user):
    watchlists = Watchlist.objects.filter(user=user)
    for watchlist in watchlists:
        print(watchlist.id, watchlist.watchlist_name)

def select_watchlist(user):
    watchlist_id = input("Enter the ID of the watchlist you want to copy: ")
    try:
        watchlist = Watchlist.objects.get(id=watchlist_id, user=user)
        return watchlist
    except Watchlist.DoesNotExist:
        print("Watchlist does not exist.")
        return None

def select_or_create_watchlist(user):
    watchlist_id = input("Enter the ID of the watchlist you want to copy to, or enter 'new' to create a new watchlist: ")
    if watchlist_id.lower() == 'new':
        watchlist_name = input("Enter the name for the new watchlist: ")
        new_watchlist = Watchlist.objects.create(user=user, watchlist_name=watchlist_name)
        return new_watchlist
    try:
        watchlist = Watchlist.objects.get(id=watchlist_id, user=user)
        return watchlist
    except Watchlist.DoesNotExist:
        print("Watchlist does not exist.")
        return None

def copy_watchlist_entries(source_watchlist, destination_watchlist):
    source_entries = source_watchlist.entries.all()
    destination_entries = destination_watchlist.entries.all()
    
    for source_entry in source_entries:
        if source_entry.movie not in [entry.movie for entry in destination_entries]:
            WatchlistEntry.objects.create(watchlist=destination_watchlist, movie=source_entry.movie)
        else:
            print(f"Movie '{source_entry.movie.title}' already exists in the destination watchlist.")

def main():
    print("List of users:")
    list_users()
    source_user = select_user()
    if not source_user:
        return
    
    print("List of watchlists for selected user:")
    list_watchlists(source_user)
    source_watchlist = select_watchlist(source_user)
    if not source_watchlist:
        return
    
    print("List of users to copy watchlist entries to:")
    list_users()
    destination_user = select_user()
    if not destination_user:
        return
    
    print("List of watchlists for selected user:")
    list_watchlists(destination_user)
    destination_watchlist = select_or_create_watchlist(destination_user)
    if not destination_watchlist:
        return
    
    copy_watchlist_entries(source_watchlist, destination_watchlist)
    print("Watchlist entries copied successfully!")

if __name__ == "__main__":
    main()
