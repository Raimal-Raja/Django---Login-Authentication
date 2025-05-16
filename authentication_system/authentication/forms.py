from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    bio = forms.CharField(max_length=500, required=False, widget=forms.Textarea)
    location = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone_number", "bio", "location", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            logger.info(f"Created user: {user.username} with email: {user.email}")
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data["phone_number"]
            profile.bio = self.cleaned_data["bio"]
            profile.location = self.cleaned_data["location"]
            profile.save()
            logger.info(f"{'Created' if created else 'Updated'} UserProfile for user: {user.username} with bio: {profile.bio}")
            print(f"DEBUG: Saved user {user.username} with profile bio: {profile.bio}")  # Temporary debug
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'birth_date', 'bio', 'location', 'website', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }