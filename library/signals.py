"""
library/signals.py - Django signals for library-related events

Automatically sends emails when books are issued, returned, or reserved.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import IssueBook, Reservation
from .emails import (
    send_book_issued_email,
    send_book_returned_email,
    send_book_reserved_email,
    send_review_reminder_email,
)


@receiver(post_save, sender=IssueBook)
def send_email_on_book_issue(sender, instance, created, **kwargs):
    """
    Send email confirmation when a book is issued to a student.
    
    This signal is triggered when an IssueBook record is created.
    """
    if created and instance.return_date is None:
        # New issue - send book issued email
        send_book_issued_email(instance)
    elif instance.return_date is not None and not kwargs.get('skip_email'):
        # Book has been returned - send return confirmation
        send_book_returned_email(instance)
        
        # Send review reminder email
        send_review_reminder_email(instance)


@receiver(post_save, sender=Reservation)
def send_email_on_book_reservation(sender, instance, created, **kwargs):
    """
    Send email confirmation when a book is reserved.
    
    This signal is triggered when a Reservation record is created.
    """
    if created:
        # New reservation - send confirmation email
        send_book_reserved_email(instance)
