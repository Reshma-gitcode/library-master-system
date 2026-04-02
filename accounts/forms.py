"""
accounts/forms.py - Registration form for students

Handles new student account creation with password confirmation
and duplicate email validation.
"""

from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterForm(forms.ModelForm):
   

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
        validators=[validate_password],
        help_text="Must be at least 8 characters.",
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
            "email":    forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
        }

    def clean_email(self):
        """Ensure email is provided and not already registered."""
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        """Ensure both passwords match."""
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned
