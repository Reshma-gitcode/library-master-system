"""
accounts/urls.py - URL routing for the accounts app

Author: Library Dev Team
"""

from django.urls import path
from .views import register

urlpatterns = [
    path('register/', register, name='register'),
]
