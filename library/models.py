"""
library/models.py

Data models for the LibraryMaster application.
Defines Book, IssueBook, and Reservation entities.

Author: Library Dev Team
"""

from django.db import models
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta

# Reference to the custom user model defined in accounts app
User = settings.AUTH_USER_MODEL

# Fine rate per overdue day (in rupees)
FINE_PER_DAY = 5

# Default loan period in days
LOAN_PERIOD_DAYS = 7

# Reservation expiry period in days
RESERVATION_EXPIRY_DAYS = 3


class Book(models.Model):
    """
    Represents a book in the library catalogue.

    Each book tracks its title, author, genre, optional ISBN,
    and current available quantity.
    """

    title    = models.CharField(max_length=200)
    author   = models.CharField(max_length=100)
    genre    = models.CharField(max_length=100)
    isbn     = models.CharField(
        max_length=13,
        unique=True,
        null=True,
        blank=True,
        help_text="10 or 13 digit ISBN number (optional)"
    )
    quantity = models.IntegerField(default=0, help_text="Number of copies available")

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

    @property
    def is_available(self):
        """Returns True if at least one copy is available for issue."""
        return self.quantity > 0


class IssueBook(models.Model):
    """
    Tracks a book being issued to a student.

    Records issue date, due date, return date, and any applicable fine.
    Fine is calculated at ₹5 per day after the due date.
    """

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    book        = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issuebook_set')
    issue_date  = models.DateField(auto_now_add=True)
    due_date    = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    fine        = models.IntegerField(default=0, help_text="Fine amount in rupees")
    fine_paid   = models.BooleanField(default=False)

    class Meta:
        indexes = [
            # Optimise the common query: active issues for a user+book
            models.Index(fields=['user', 'book', 'return_date']),
        ]

    def save(self, *args, **kwargs):
        # Auto-set due date on first save if not provided
        if not self.due_date:
            self.due_date = now().date() + timedelta(days=LOAN_PERIOD_DAYS)
        super().save(*args, **kwargs)

    def calculate_fine(self):
        """
        Calculate the overdue fine based on return date (or today if not yet returned).
        Returns 0 if the book was returned on time.
        """
        check_date = self.return_date or now().date()
        if check_date > self.due_date:
            overdue_days = (check_date - self.due_date).days
            return overdue_days * FINE_PER_DAY
        return 0

    @property
    def is_overdue(self):
        """Returns True if the book is currently overdue and not yet returned."""
        if self.return_date:
            return False
        return now().date() > self.due_date

    def __str__(self):
        return f"{self.user.username} — {self.book.title}"


class Reservation(models.Model):
    """
    Represents a student's reservation for an out-of-stock book.

    When the book becomes available (returned by another student),
    it is automatically issued to the first person in the reservation queue.
    Reservations expire after RESERVATION_EXPIRY_DAYS days.
    """

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book        = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        # A student can only have one active reservation per book
        unique_together = ('user', 'book')
        ordering = ['reserved_at']

    def save(self, *args, **kwargs):
        # Auto-set expiry on first save
        if not self.expires_at:
            self.expires_at = now() + timedelta(days=RESERVATION_EXPIRY_DAYS)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} reserved '{self.book.title}'"
