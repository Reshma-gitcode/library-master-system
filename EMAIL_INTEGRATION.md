# Email Integration Guide for LibraryMaster

This guide explains how to set up and use the email integration system in LibraryMaster.

## Overview

LibraryMaster includes comprehensive email integration that automatically sends emails for various events:

- **Account Events**: Welcome emails for new students, librarian account creation
- **Book Issues**: Confirmation when books are issued
- **Book Returns**: Confirmation when books are returned
- **Overdue Books**: Reminders and alerts for overdue books
- **Reservations**: Confirmation of reservations and notifications when books become available
- **Reviews**: Reminders to review books after returning them

## Setup Instructions

### 1. Install Dependencies

The required packages are already listed in `requirements.txt`. Ensure they're installed:

```bash
pip install -r requirements.txt
```

Key packages:
- `django` - Core framework
- `python-dotenv` - Environment variable management

### 2. Configure Email Settings

#### Option A: Gmail (Recommended for Development)

1. **Get an App Password**:
   - Go to [Google Account Security Settings](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled
   - Generate an [App Password](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or your device)

2. **Update your `.env` file**:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password_here
   ```

#### Option B: Other Email Providers

**Outlook/Microsoft 365**:
```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@outlook.com
EMAIL_HOST_PASSWORD=your_password
```

**SendGrid**:
```env
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your_sendgrid_api_key
```

#### Option C: Development/Testing

**Console Backend** (prints emails to console):
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**File Backend** (saves emails to files):
```env
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/path/to/email-logs
```

### 3. Update Settings

The email configuration is already in `myproject/settings.py`. Environment variables are loaded automatically:

```python
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
```

## Email Events and Triggers

### 1. Student Registration

**When**: A new student account is created via `/register/`
**Recipient**: New student email
**Template**: `welcome.html`
**Content**: Welcome message and account details

**Triggered by**: `post_save` signal on User model (role='student')

### 2. Librarian Account Creation

**When**: A librarian account is created via management command
**Command**: `python manage.py create_librarian <username> <email> <password>`
**Recipient**: Librarian email
**Template**: `librarian_account.html`
**Content**: Login credentials and account privileges

**Example**:
```bash
python manage.py create_librarian lib1 librarian@example.com SecurePass123!
```

### 3. Book Issued

**When**: A student issues a book
**Recipient**: Student email
**Template**: `book_issued.html`
**Content**: Book details, issue date, due date, late fees

**Triggered by**: `post_save` signal on IssueBook model (when created)

### 4. Book Returned

**When**: A student returns a book
**Recipient**: Student email
**Template**: `book_returned.html`
**Content**: Return confirmation, fine details (if applicable)

**Triggered by**: `post_save` signal on IssueBook model (when return_date is set)

### 5. Overdue Reminders

**When**: Scheduled via management command
**Command**: `python manage.py send_overdue_reminders`
**Recipient**: Students with overdue books
**Template**: `overdue_reminder.html`
**Content**: Book details, days overdue, accrued fine

**Setup as Cron Job**:
```bash
# Send reminders daily at 9 AM
0 9 * * * cd /path/to/LibraryMaster && python manage.py send_overdue_reminders
```

**With Docker/Celery**: Use task scheduler like Celery Beat

### 6. Book Reserved

**When**: A student reserves a book
**Recipient**: Student email
**Template**: `book_reserved.html`
**Content**: Reservation confirmation, expiry date

**Triggered by**: `post_save` signal on Reservation model (when created)

### 7. Reservation Available

**When**: A reserved book is issued to a student (automatic processing)
**Recipient**: Student email
**Template**: `reservation_available.html`
**Content**: Book issued confirmation, due date

**Triggered by**: Manual code in `edit_book` view

### 8. Review Reminder

**When**: A book is returned
**Recipient**: Student email
**Template**: `review_reminder.html`
**Content**: Request to review the book

**Triggered by**: `post_save` signal on IssueBook model (after return)

## Email Templates

All templates are stored in `templates/emails/`:

| Template | Purpose |
|----------|---------|
| `welcome.html` | Student registration welcome |
| `librarian_account.html` | Librarian account credentials |
| `book_issued.html` | Book issue confirmation |
| `book_returned.html` | Book return confirmation |
| `overdue_reminder.html` | Overdue book reminder |
| `fine_alert.html` | Fine notification |
| `book_reserved.html` | Reservation confirmation |
| `reservation_available.html` | Reserved book available |
| `reservation_expired.html` | Reservation expiration notice |
| `review_reminder.html` | Request for book review |
| `password_reset.html` | Password reset link |
| `verify_email.html` | Email verification |

## Manual Email Sending

You can send emails manually in views or management commands:

### From Views

```python
from library.emails import send_book_issued_email

@login_required
def issue_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    # ... issue logic ...
    issue = IssueBook.objects.create(user=request.user, book=book)
    send_book_issued_email(issue)  # Send email
    return redirect('my_books')
```

### From Management Commands

```python
from django.core.management.base import BaseCommand
from library.models import IssueBook
from library.emails import send_fine_alert_email

class Command(BaseCommand):
    def handle(self, *args, **options):
        pending_fines = IssueBook.objects.filter(fine__gt=0, fine_paid=False)
        for issue in pending_fines:
            send_fine_alert_email(issue)
```

## Testing Email Configuration

### Test 1: Django Shell

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from LibraryMaster',
    settings.EMAIL_HOST_USER,
    ['recipient@example.com'],
    fail_silently=False,
)
```

### Test 2: View Test

```bash
# Using console backend (default in development)
python manage.py runserver
# Register a new student account
# Check console output for email content
```

### Test 3: Management Command

```bash
# Create a librarian account and check email
python manage.py create_librarian testlib testlib@example.com Pass123!

# Send overdue reminders (test run)
python manage.py send_overdue_reminders --dry-run
```

## Troubleshooting

### Email Not Sending

1. **Check EMAIL_BACKEND**:
   ```python
   from django.conf import settings
   print(settings.EMAIL_BACKEND)
   ```

2. **Verify SMTP Settings**:
   ```bash
   python manage.py shell
   from django.core.mail import get_connection
   conn = get_connection()
   print(conn)
   ```

3. **Enable Debug Mode**:
   ```python
   # In settings.py temporarily
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```

### Gmail Authentication Failed

- Verify 2-Step Verification is enabled
- Check App Password is correctly generated
- Ensure EMAIL_HOST_USER matches the Gmail account
- Check that "Less secure app access" is not blocking (for older accounts)

### Template Not Found

- Verify template path: `templates/emails/<template_name>.html`
- Check TEMPLATES setting in `settings.py`
- Run: `python manage.py findstatic --list | grep emails`

### Emails Not Being Sent (Silent Fail)

By default, emails fail silently. To debug:

```python
# In your email function
send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False,  # Change to False to see errors
)
```

## Production Deployment

### Using Gmail in Production

⚠️ **Warning**: Using personal Gmail accounts in production is not recommended.

For production, consider:
- **SendGrid**: Professional email service
- **AWS SES**: Amazon email service
- **Mailgun**: Email API service
- **Custom SMTP**: Your organization's mail server

### Setting Up SendGrid

1. Install django-sendgrid:
   ```bash
   pip install sendgrid-django
   ```

2. Update `settings.py`:
   ```python
   EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
   SENDGRID_SANDBOX_MODE_IN_DEBUG = False
   ```

3. Add to `.env`:
   ```env
   SENDGRID_API_KEY=your_sendgrid_api_key
   ```

### Rate Limiting

For high-volume emails, implement:

```python
# Use Celery for async emails
# Install: pip install celery django-celery-beat

# In tasks.py
from celery import shared_task
from library.emails import send_book_issued_email

@shared_task
def send_issue_email_async(issue_id):
    from library.models import IssueBook
    issue = IssueBook.objects.get(id=issue_id)
    send_book_issued_email(issue)
```

## Email Customization

### Modifying Templates

Edit template files in `templates/emails/` to customize:
- Email subject line (in code)
- Email body content (in HTML template)
- Colors, branding, styling

Example: Update `welcome.html` to include your library's logo:
```html
<img src="https://yourdomain.com/logo.png" alt="LibraryMaster" style="max-width: 200px;">
```

### Custom Email Functions

Create new email functions in `accounts/emails.py` or `library/emails.py`:

```python
# In library/emails.py
def send_custom_email(user, custom_data):
    context = {
        'user': user,
        'custom_data': custom_data,
        'site_name': 'LibraryMaster',
    }
    
    subject = 'Custom Email Subject'
    html_message = render_to_string('emails/custom.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.EMAIL_HOST_USER,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )
```

## Logging Email Activity

Add email logging to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'email.log',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Best Practices

1. **Always use `fail_silently=True`** in production to prevent blocking user requests
2. **Use async task queues** (Celery) for high-volume emails
3. **Include unsubscribe links** in batch emails (future enhancement)
4. **Monitor email delivery** using SPF, DKIM, DMARC records
5. **Test templates** before deploying to production
6. **Keep sensitive data** (passwords, tokens) out of version control
7. **Use environment variables** for all credentials
8. **Implement retry logic** for failed emails

## Support

For issues or questions:
1. Check this documentation
2. Review Django email documentation: https://docs.djangoproject.com/en/5.2/topics/email/
3. Check email provider documentation
4. Review signal handler implementation in `accounts/signals.py` and `library/signals.py`

---

**Last Updated**: April 2024
**Email Integration Version**: 1.0
