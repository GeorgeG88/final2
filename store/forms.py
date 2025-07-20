from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, Review

# Form for user registration using Django's built-in User model
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Require email field
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # Fields to include in the form

# Form for user login using Django's AuthenticationForm
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))  # Custom widget for username
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))  # Custom widget for password

# Form for updating user information
class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Only allow updating username and email
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)  # Remove password field from the form

# Form for updating user profile (custom fields)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone', 'address']  # Fields to update in profile

# Form for submitting a product review
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']  # Fields to include in the review form
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),  # Limit rating input
            'comment': forms.Textarea(attrs={'rows': 3})  # Set textarea size for comment
        }