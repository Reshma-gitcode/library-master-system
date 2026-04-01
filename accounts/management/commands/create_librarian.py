"""
accounts/management/commands/create_librarian.py

Custom management command to create a librarian account.

Usage:
    python manage.py create_librarian <username> <email> <password>

Example:
    python manage.py create_librarian librarian1 lib@library.com securepass123

Note:
    Students self-register via /register/.
    Librarian accounts must be created through this command to prevent
    students from self-assigning the admin role.

Author: Library Dev Team
"""

from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Create a librarian (admin) account"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username for the librarian")
        parser.add_argument("email",    type=str, help="Email address")
        parser.add_argument("password", type=str, help="Account password")

    def handle(self, *args, **options):
        username = options["username"]
        email    = options["email"]
        password = options["password"]

        # Check for duplicate username
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'"{ username }" already exists.'))
            return

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="admin",
            is_staff=True,  # grants access to Django admin panel
        )

        self.stdout.write(self.style.SUCCESS(f"Librarian account \"{ username }\" created successfully."))
