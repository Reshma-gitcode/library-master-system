"""
accounts/urls.py - URL routing for the accounts app

"""

from django.urls import path
from .views import register

urlpatterns = [
    path('register/', register, name='register'),
]
