"""
myproject/urls.py - Root URL configuration for LibraryMaster

Routes:
  /           → library app (book catalogue, issues, reservations)
  /register/  → student registration
  /login/     → Django built-in login view
  /logout/    → Django built-in logout view
  /admin/     → Django admin panel

Author: Library Dev Team
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Django admin panel (for superuser access)
    path('admin/', admin.site.urls),

    # Library app routes
    path('', include('library.urls')),

    # Accounts app routes (registration)
    path('', include('accounts.urls')),

    # Auth routes (Django built-in)
    path('login/',  auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
