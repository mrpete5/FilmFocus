"""
Name of code artifact: forms.py
Brief description: This python file is responsible for handling user registration
Programmer’s name: Bill
Date the code was created: 10/4/2023
Dates the code was revised: 10/4/2023

"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user