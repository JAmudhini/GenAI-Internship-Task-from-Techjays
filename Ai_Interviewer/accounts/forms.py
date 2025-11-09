from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CandidateProfile

class HRRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'HR'
        if commit:
            user.save()
        return user

class CandidateRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'CANDIDATE'
        if commit:
            user.save()
            CandidateProfile.objects.create(user=user)
        return user
