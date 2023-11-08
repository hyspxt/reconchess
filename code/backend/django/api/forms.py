from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    #checks if email already exists in the database, will be run in form validation
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use!")
        return email
    
    class Meta:
        model=User
        fields = ['username','email','password1','password2'] 
