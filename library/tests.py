from django.contrib.auth import get_user_model
from django.test import TestCase
from datetime import date, timedelta

from .models import Book, IssueBook


class IssueBookFineTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='student1', password='testpass')
        self.book = Book.objects.create(title='Test Book', author='Author', genre='Fiction', quantity=1)

    def test_calculate_fine_for_returned_issue(self):
        due_date = date.today() - timedelta(days=3)
        issue = IssueBook.objects.create(
            user=self.user,
            book=self.book,
            issue_date=date.today() - timedelta(days=10),
            due_date=due_date,
            return_date=date.today(),
            fine=0,
        )
        self.assertEqual(issue.calculate_fine(), 15)
        self.assertEqual(issue.current_fine, 0)

    def test_current_fine_for_active_overdue_issue(self):
        due_date = date.today() - timedelta(days=4)
        issue = IssueBook.objects.create(
            user=self.user,
            book=self.book,
            issue_date=date.today() - timedelta(days=11),
            due_date=due_date,
            return_date=None,
        )
        self.assertEqual(issue.calculate_fine(), 20)
        self.assertEqual(issue.current_fine, 20)

    def test_current_fine_for_active_on_time_issue(self):
        issue = IssueBook.objects.create(
            user=self.user,
            book=self.book,
            issue_date=date.today() - timedelta(days=2),
            due_date=date.today() + timedelta(days=5),
            return_date=None,
        )
        self.assertEqual(issue.calculate_fine(), 0)
        self.assertEqual(issue.current_fine, 0)
