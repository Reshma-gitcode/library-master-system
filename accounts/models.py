"""
accounts/models.py - Custom user model for LibraryMaster

"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access.

    Roles:
      - 'admin'   : Librarian — full access to book management and reports
      - 'student' : Student   — can browse, issue, and reserve books

    Note: Librarian accounts are created via the create_librarian management
    command. Students self-register through the /register/ page.
    """

    ROLE_CHOICES = [
        ('admin',   'Librarian'),
        ('student', 'Student'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
    )

    def is_librarian(self):
        """Returns True if this user is a librarian."""
        return self.role == 'admin'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
