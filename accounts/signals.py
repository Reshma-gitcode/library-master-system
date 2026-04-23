"""
accounts/signals.py - Django signals for account-related events

Automatically sends emails when certain account events occur.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .emails import send_registration_email, send_new_user_notification_email
from library.models import Notification


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

        # Notify all existing users about the new registration
        existing_users = User.objects.exclude(id=instance.id)
        notification_message = f"New student '{instance.username}' has joined LibraryMaster!"

        # Create in-app notifications for all existing users
        notifications = []
        for user in existing_users:
            notifications.append(
                Notification(user=user, message=notification_message)
            )

        # Bulk create notifications for efficiency
        if notifications:
            Notification.objects.bulk_create(notifications)

        # Send email notifications to all existing users (limit to avoid spam)
        # For now, let's just send to a few users to test
        email_recipients = existing_users[:3]  # Limit to first 3 users for testing

        for user in email_recipients:
            try:
                send_new_user_notification_email(instance, user)
            except Exception as e:
                # Log error but don't break the registration process
                print(f"Failed to send notification email to {user.email}: {e}")
                pass
