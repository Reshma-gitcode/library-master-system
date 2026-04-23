# Email Integration Setup Checklist

Use this checklist to verify your email integration is properly configured.

## Pre-Setup ✓

- [ ] You have a `.env` file (or ready to create one)
- [ ] You have an email account (Gmail, Outlook, or other SMTP)
- [ ] Django project is running without errors

## Configuration Setup

### Step 1: Environment File
- [ ] Copied `.env.example` to `.env` (or created new `.env`)
- [ ] Added `EMAIL_BACKEND` setting
- [ ] Added `EMAIL_HOST` setting
- [ ] Added `EMAIL_PORT` setting
- [ ] Added `EMAIL_USE_TLS` setting
- [ ] Added `EMAIL_HOST_USER` setting
- [ ] Added `EMAIL_HOST_PASSWORD` setting (if using SMTP backend)

### Step 2: Test Backend Selection
- [ ] Chose test backend (Console / File / SMTP)
- [ ] Console backend: Good for initial testing
- [ ] File backend: Good for reviewing emails
- [ ] SMTP backend: Only after credentials are verified

### Step 3: Email Credentials
If using SMTP (Gmail/Outlook):
- [ ] Gmail: Generated App Password from Google Account
- [ ] Outlook: Have account password ready
- [ ] Other SMTP: Have server details ready
- [ ] Credentials are correctly entered in `.env`

## Django Setup Verification

### Files Created
- [ ] `accounts/emails.py` exists and contains email functions
- [ ] `library/emails.py` exists and contains email functions
- [ ] `accounts/signals.py` exists
- [ ] `library/signals.py` exists
- [ ] `library/management/commands/send_overdue_reminders.py` exists

### Templates Created
- [ ] `templates/emails/welcome.html` exists
- [ ] `templates/emails/book_issued.html` exists
- [ ] `templates/emails/book_returned.html` exists
- [ ] All 12 email templates exist in `templates/emails/`

### Configuration Files
- [ ] `.env.example` exists
- [ ] `.env` exists and is configured
- [ ] `myproject/settings.py` has email configuration

### Documentation
- [ ] `EMAIL_INTEGRATION.md` exists
- [ ] `QUICK_START_EMAIL.md` exists
- [ ] This checklist file exists

## Signal Registration Verification

Run this in Python shell to verify signals are registered:

```bash
python manage.py shell
```

```python
from django.db.models.signals import post_save
from accounts.models import User
from library.models import IssueBook, Reservation

# Check signal receivers
receivers = post_save.receivers_cache
print("Receivers:", receivers)
```

- [ ] Signals are registered without errors
- [ ] No import errors in accounts/signals.py
- [ ] No import errors in library/signals.py

## Test Scenarios

### Test 1: Console Backend
- [ ] Set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
- [ ] Run development server: `python manage.py runserver`
- [ ] Create new student account at `/register/`
- [ ] Check console output for welcome email
- [ ] Verify email contains correct user information

### Test 2: File Backend
- [ ] Set `EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend`
- [ ] Create `./email-logs` directory if it doesn't exist
- [ ] Register a new student
- [ ] Check for `.log` files in `./email-logs/`
- [ ] Open log file and verify email content

### Test 3: Django Shell
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

result = send_mail(
    'Test Subject',
    'Test body message',
    settings.EMAIL_HOST_USER,
    ['test@example.com'],
    fail_silently=False,
)
print(f"Email sent: {result}")
```

- [ ] send_mail() returns 1 (success)
- [ ] No exceptions raised
- [ ] Email appears in backend (console/file/SMTP)

### Test 4: Management Command (Dry Run)
```bash
python manage.py send_overdue_reminders --dry-run
```

- [ ] Command runs without errors
- [ ] Shows list of users with overdue books
- [ ] No emails are actually sent (dry-run mode)

### Test 5: Librarian Account Creation
```bash
python manage.py create_librarian testlib test@example.com Password123!
```

- [ ] Account created successfully
- [ ] Email sent (check backend)
- [ ] Welcome email contains username and password
- [ ] Email template is professional-looking

### Test 6: Book Issue/Return Emails
- [ ] Issue a book
- [ ] Check if issue confirmation email was sent (console/file/SMTP)
- [ ] Return the book
- [ ] Check if return confirmation email was sent
- [ ] Verify email contains book details and dates

### Test 7: Book Reservation Email
- [ ] Reserve a book that's not available
- [ ] Check if reservation email was sent
- [ ] Verify email contains book title and reservation details

## Verification Commands

Run these to verify setup:

```bash
# Check Python packages
pip list | grep -i django

# Check .env file exists
ls -la .env

# Check email templates
ls -la templates/emails/

# Check email modules
python -c "from accounts.emails import send_registration_email; print('✓ Accounts email module OK')"
python -c "from library.emails import send_book_issued_email; print('✓ Library email module OK')"

# Check signals
python -c "import accounts.signals; import library.signals; print('✓ Signals OK')"

# Run Django check
python manage.py check

# List installed apps
python manage.py shell -c "from django.conf import settings; print(settings.INSTALLED_APPS)"
```

- [ ] All commands run without errors
- [ ] No missing dependencies
- [ ] Settings check passes

## Production Readiness

### Before deploying to production:
- [ ] Email templates customized with your branding
- [ ] Switched from test backend to production backend
- [ ] Set up email service (SendGrid / AWS SES / etc.)
- [ ] Configured proper email domain/SPF/DKIM records
- [ ] Set up email logging/monitoring
- [ ] Tested high-volume email sending
- [ ] Scheduled `send_overdue_reminders` command
- [ ] Set DEBUG=False in production
- [ ] Used secure SMTP credentials (not committed to repo)

## Common Issues and Solutions

### ❌ Issue: "Email backend not found"
**Solution**: Verify EMAIL_BACKEND value in .env

### ❌ Issue: "Module not found" when importing emails
**Solution**: Make sure files are in correct directories (accounts/emails.py, library/emails.py)

### ❌ Issue: "Template not found"
**Solution**: Check templates/emails/ directory exists with correct templates

### ❌ Issue: "Signal not being triggered"
**Solution**: Run Django shell and verify signals are registered

### ❌ Issue: "Gmail authentication failed"
**Solution**: Use App Password instead of account password, enable 2-Step Verification

### ❌ Issue: "Emails are silent (not sent, no error)"
**Solution**: Change `fail_silently=False` in send_mail() calls for debugging

## Next Steps

After verification:

1. **Customize Templates**
   - [ ] Add your library logo to templates
   - [ ] Update colors to match branding
   - [ ] Review and edit email copy

2. **Schedule Overdue Reminders**
   - [ ] Set up cron job: `0 9 * * * cd /path && python manage.py send_overdue_reminders`
   - [ ] Or use Celery Beat for task scheduling

3. **Production Deployment**
   - [ ] Follow production setup in EMAIL_INTEGRATION.md
   - [ ] Configure SendGrid or AWS SES
   - [ ] Set up monitoring and logging
   - [ ] Test with real users

4. **Monitor**
   - [ ] Check email delivery rates
   - [ ] Monitor bounces and failures
   - [ ] Gather user feedback

## Support Resources

- **Full Documentation**: [EMAIL_INTEGRATION.md](EMAIL_INTEGRATION.md)
- **Quick Start**: [QUICK_START_EMAIL.md](QUICK_START_EMAIL.md)
- **Django Email Docs**: https://docs.djangoproject.com/en/5.2/topics/email/
- **Email Templates**: `templates/emails/` directory

---

**Completion Status**: 
- Total Checks: _____ / _____
- Estimated Time: 30-60 minutes
- Last Updated: ✓ [Date]

**Sign-off**: 
- Setup Completed: ☐ Yes ☐ No
- Verified Working: ☐ Yes ☐ No
- Ready for Production: ☐ Yes ☐ No
