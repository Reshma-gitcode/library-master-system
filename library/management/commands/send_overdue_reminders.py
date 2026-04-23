"""
library/management/commands/send_overdue_reminders.py

Management command to send overdue book reminders to students.

Usage:
    python manage.py send_overdue_reminders

This command:
1. Finds all overdue books (not yet returned)
2. Sends reminder emails to students
3. Logs the number of emails sent

Schedule this command to run daily using a task scheduler like Celery or cron.
"""

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from library.models import IssueBook
from library.emails import send_overdue_reminder_email


class Command(BaseCommand):
    help = "Send reminder emails for overdue books"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = now().date()

        # Find all overdue issues (not yet returned)
        overdue_issues = IssueBook.objects.filter(
            return_date=None,
            due_date__lt=today
        ).select_related('user', 'book')

        count = 0
        for issue in overdue_issues:
            days_overdue = (today - issue.due_date).days

            if dry_run:
                self.stdout.write(
                    f"Would send overdue reminder to {issue.user.email} "
                    f"for '{issue.book.title}' ({days_overdue} days overdue)"
                )
            else:
                try:
                    send_overdue_reminder_email(issue, days_overdue)
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Sent reminder to {issue.user.email} "
                            f"for '{issue.book.title}'"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed to send email to {issue.user.email}: {str(e)}"
                        )
                    )

        if dry_run:
            self.stdout.write(f"\n{len(overdue_issues)} reminder(s) would be sent.")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Successfully sent {count} overdue reminder(s).")
            )
