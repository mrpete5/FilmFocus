"""
Name of code artifact: forms.py
Brief description: This Python file is responsible for handling user registration.
Programmer’s name: Bill, Mark
Date the code was created: 10/04/2023
Dates the code was revised: 10/08/2023

"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Watchlist 
from django.core.validators import MaxLengthValidator




class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'sign__input', 'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        
        # Use widgets on built in authentication fields
        username_attrs = {'class':'sign__input', 'placeholder': 'Username'}
        self.fields['username'].max_length = 30 # added to try and limit character length
        self.fields['username'].widget.attrs=username_attrs
        self.fields['username'].validators.append(MaxLengthValidator(limit_value=25)) # added to try and limit character length

        password1_attrs = {'class':'sign__input', 'placeholder': 'Password', 'type': 'password', 'id':'id_password'}
        self.fields['password1'].widget.attrs=password1_attrs
        self.fields['password1'].validators.append(MaxLengthValidator(limit_value=30)) # added to try and limit character length

        password2_attrs = {'class':'sign__input', 'placeholder': 'Confirm Password', 'type': 'password', 'id':'id_confirmationPassword'}
        self.fields['password2'].widget.attrs=password2_attrs
        self.fields['password2'].validators.append(MaxLengthValidator(limit_value=30)) # added to try and limit character length
        

class CustomAuthForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password")

    def save(self, commit=True):
        user = super(AuthenticationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Use widgets on built in authentication fields
        username_attrs = {'class':'sign__input', 'placeholder': 'Username'} 
        self.fields['username'].widget.attrs=username_attrs
        self.fields['username'].validators.append(MaxLengthValidator(limit_value=25)) # added to try and limit character length
        
        password_attrs = {'class':'sign__input', 'placeholder': 'Password', 'type': 'password', 'id':'id_password'}
        self.fields['password'].widget.attrs=password_attrs  
        self.fields['password'].validators.append(MaxLengthValidator(limit_value=30)) # added to try and limit character length  
        

class NewWatchlistForm(forms.Form):
    watchlist_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class':'wlist__input',
                                                                                                  'placeholder': 'New Watchlist Name',
                                                                                                  'type': 'text',
                                                                                                  'id':'watchlistNameInput'}))
    class Meta:
        model = Watchlist
        fields = ("watchlist_name")
    
    def save(self, commit=True):
        watchlist = Watchlist()
        watchlist.watchlist_name = self.cleaned_data['watchlist_name']
        
        if commit:
            watchlist.save()
            
        return watchlist
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # # Use widgets on built in authentication fields
        # watchlist_name_attrs = {'class':'sign__input', 'placeholder': 'Watchlist Name'} 
        # self.fields['watchlist_name'].widget.attrs=watchlist_name_attrs

class PasswordResetForm(forms.Form):
    username = forms.CharField(label="Username", max_length=25) # changed to try and limit character length

class PasswordResetConfirmForm(forms.Form):
    new_password_1 = forms.CharField(label="New Password", max_length=30) # changed to try and limit character length
    new_password_2 = forms.CharField(label="Confirm Password", max_length=30) # changed to try and limit character length

class FilterForm(forms.Form):
    genre = forms.CharField(label="Genre", max_length=255)
    streaming_provider = forms.CharField(label="Streaming Provider", max_length=255)
    year_begin = forms.IntegerField(label="Year Begin")
    year_end = forms.IntegerField(label="Year End")
    imdb_begin = forms.FloatField(label="IMDB Rating Begin")
    imdb_end = forms.FloatField(label="IMDB Rating End")


class WatchlistFilterForm(FilterForm):
    watchlist_id = forms.IntegerField(label="Wishlist ID")

class CatalogFilterForm(FilterForm):
    pass

# from .models import Watchlist

# class NewWatchlistForm(forms.Form):

#     watchlist_name = forms.CharField()

#     def save(self, user, commit=True):
#         watchlist = Watchlist(user=user, name=self.cleaned_data['name'])
#         if commit:
#             watchlist.save()
#             return watchlist
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Use widgets on built in authentication fields
#         watchlist_name_attrs = {'class':'sign__input', 'placeholder': 'Watchlist Name'} 
#         self.fields['watchlist_name'].widget.attrs=watchlist_name_attrs