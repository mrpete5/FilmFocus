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
        self.fields['username'].widget.attrs=username_attrs
        
        password1_attrs = {'class':'sign__input', 'placeholder': 'Password', 'type': 'password', 'id':'id_password'}
        self.fields['password1'].widget.attrs=password1_attrs

        password2_attrs = {'class':'sign__input', 'placeholder': 'Confirm Password', 'type': 'password', 'id':'id_confirmationPassword'}
        self.fields['password2'].widget.attrs=password2_attrs
        

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
        
        password_attrs = {'class':'sign__input', 'placeholder': 'Password', 'type': 'password', 'id':'id_password'}
        self.fields['password'].widget.attrs=password_attrs    
        

class NewWatchlistForm(forms.Form):
    watchlist_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class':'wlist__input', 'placeholder': 'Watchlist Name'}))
    
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
    username = forms.CharField(label="Username", max_length=254)

class PasswordResetConfirmForm(forms.Form):
    new_password_1 = forms.CharField(label="New Password", max_length=254)
    new_password_2 = forms.CharField(label="Confirm Password", max_length=254)


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