"""
accounts/signals.py - Django signals for account-related events

Automatically sends emails when certain account events occur.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .emails import send_registration_email


@receiver(post_save, sender=User)
def send_welcome_email_on_register(sender, instance, created, **kwargs):
    """
    Send welcome email when a new student account is created.
    
    This signal is triggered whenever a User is created. We only send
    an email for newly created student accounts (not librarians).
    """
    if created and instance.role == 'student':
        # Send welcome email to new student
        send_registration_email(instance)
