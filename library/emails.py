"""
library/emails.py - Email utilities for book-related notifications

Handles sending emails for book issues, reservations, fines, and reviews.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_book_issued_email(issue):
    """
    Send confirmation email when a book is issued to a student.
    
    Args:
        issue: IssueBook instance
    """
    context = {
        'user': issue.user,
        'book': issue.book,
        'issue_date': issue.issue_date,
        'due_date': issue.due_date,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Book Issued: {issue.book.title}'
    html_message = render_to_string('emails/book_issued.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [issue.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_book_returned_email(issue):
    """
    Send confirmation email when a book is returned.
    
    Args:
        issue: IssueBook instance
    """
    context = {
        'user': issue.user,
        'book': issue.book,
        'return_date': issue.return_date,
        'fine': issue.fine,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Book Returned: {issue.book.title}'
    html_message = render_to_string('emails/book_returned.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [issue.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_overdue_reminder_email(issue, days_overdue):
    """
    Send reminder email for overdue books.
    
    Args:
        issue: IssueBook instance
        days_overdue: Number of days the book is overdue
    """
    context = {
        'user': issue.user,
        'book': issue.book,
        'due_date': issue.due_date,
        'days_overdue': days_overdue,
        'fine_per_day': 5,  # Should match FINE_PER_DAY from models
        'total_fine': days_overdue * 5,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Overdue Book Reminder: {issue.book.title}'
    html_message = render_to_string('emails/overdue_reminder.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [issue.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_fine_alert_email(issue):
    """
    Send alert email for pending fines.
    
    Args:
        issue: IssueBook instance with pending fine
    """
    context = {
        'user': issue.user,
        'book': issue.book,
        'fine': issue.fine,
        'due_date': issue.due_date,
        'return_date': issue.return_date,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Library Fine Alert: Rs.{issue.fine}'
    html_message = render_to_string('emails/fine_alert.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [issue.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_book_reserved_email(reservation):
    """
    Send confirmation email when a book is reserved.
    
    Args:
        reservation: Reservation instance
    """
    context = {
        'user': reservation.user,
        'book': reservation.book,
        'reserved_at': reservation.reserved_at,
        'expires_at': reservation.expires_at,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Book Reserved: {reservation.book.title}'
    html_message = render_to_string('emails/book_reserved.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [reservation.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_reservation_available_email(reservation, issue):
    """
    Send email when a reserved book becomes available and is issued.
    
    Args:
        reservation: Reservation instance (about to be processed)
        issue: IssueBook instance (newly created)
    """
    context = {
        'user': reservation.user,
        'book': reservation.book,
        'issue_date': issue.issue_date,
        'due_date': issue.due_date,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Reserved Book Available: {reservation.book.title}'
    html_message = render_to_string('emails/reservation_available.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [reservation.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_reservation_expired_email(reservation):
    """
    Send email when a reservation expires due to inactivity.
    
    Args:
        reservation: Reservation instance
    """
    context = {
        'user': reservation.user,
        'book': reservation.book,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Reservation Expired: {reservation.book.title}'
    html_message = render_to_string('emails/reservation_expired.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [reservation.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_review_reminder_email(issue):
    """
    Send reminder email asking user to review a book they've read.
    
    Args:
        issue: IssueBook instance (returned)
    """
    context = {
        'user': issue.user,
        'book': issue.book,
        'return_date': issue.return_date,
        'site_name': 'LibraryMaster',
    }
    
    subject = f'Review the Book You Read: {issue.book.title}'
    html_message = render_to_string('emails/review_reminder.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [issue.user.email],
        html_message=html_message,
        fail_silently=True,
    )
