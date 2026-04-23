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
        settings.DEFAULT_FROM_EMAIL,
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
        settings.DEFAULT_FROM_EMAIL,
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
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_new_user_notification_email(new_user, existing_user):
    """
    Send email notification to an existing user about a new registration.

    Args:
        new_user: The newly registered User object
        existing_user: The existing user to notify
    """
    context = {
        'new_user': new_user,
        'existing_user': existing_user,
        'site_name': 'LibraryMaster',
    }

    subject = f'New Student Joined LibraryMaster!'
    html_message = render_to_string('emails/new_user_notification.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [existing_user.email],
        html_message=html_message,
        fail_silently=True,
    )
