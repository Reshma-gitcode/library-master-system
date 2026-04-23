"""
accounts/emails.py - Email utilities for LibraryMaster

Handles sending emails for various account-related events.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_registration_email(user):
    """
    Send a welcome email to a newly registered user.
    """
    context = {
        'user': user,
        'site_name': 'LibraryMaster',
    }
    
    subject = 'Welcome to LibraryMaster!'
    html_message = render_to_string('emails/welcome.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_password_reset_email(user, reset_link):
    """
    Send password reset email to user.
    
    Args:
        user: User object
        reset_link: The reset URL to include in the email
    """
    context = {
        'user': user,
        'reset_link': reset_link,
        'site_name': 'LibraryMaster',
    }
    
    subject = 'LibraryMaster - Password Reset Request'
    html_message = render_to_string('emails/password_reset.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_account_verification_email(user, verification_link):
    """
    Send account verification email.
    
    Args:
        user: User object
        verification_link: The verification URL to include in the email
    """
    context = {
        'user': user,
        'verification_link': verification_link,
        'site_name': 'LibraryMaster',
    }
    
    subject = 'LibraryMaster - Verify Your Email'
    html_message = render_to_string('emails/verify_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_librarian_account_email(user, temporary_password):
    """
    Send librarian account creation email with temporary credentials.
    
    Args:
        user: Librarian user object
        temporary_password: Temporary password for initial login
    """
    context = {
        'user': user,
        'temporary_password': temporary_password,
        'login_url': '/login/',
        'site_name': 'LibraryMaster',
    }
    
    subject = 'LibraryMaster - Your Librarian Account'
    html_message = render_to_string('emails/librarian_account.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )
