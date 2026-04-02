"""
accounts/views.py - Authentication views for LibraryMaster

Handles student self-registration.
Login and logout are handled by Django's built-in auth views.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm


def register(request):
    """
    Student registration view.

    All self-registered accounts are assigned the 'student' role.
    Librarian accounts must be created via: python manage.py create_librarian
    """
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.role = 'student'  # enforce student role on self-registration
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'auth/register.html', {'form': form})
