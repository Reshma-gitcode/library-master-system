# Email Integration - Quick Start Guide

## What's Been Set Up

Your LibraryMaster project now has full email integration with:
- ✅ Automatic welcome emails for new students
- ✅ Librarian account notification emails
- ✅ Book issue/return confirmations
- ✅ Overdue book reminders
- ✅ Fine alert notifications
- ✅ Reservation confirmation and available notifications
- ✅ Review reminder emails
- ✅ Professional HTML email templates

## Quick Start (5 Minutes)

### Step 1: Configure Email in `.env`

Copy `.env.example` to `.env` and choose your email provider:

**For Gmail** (recommended for testing):
```bash
cp .env.example .env
```

Edit `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
```

Get your Gmail App Password:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Generate an [App Password](https://myaccount.google.com/apppasswords)
4. Use that password in the `.env` file

### Step 2: Test Configuration

**Option A: Console Backend** (easiest for testing):
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
This prints emails to your console.

**Option B: Gmail** (as configured above)

**Option C: File Backend** (saves emails):
```env
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=./email-logs
```

### Step 3: Test Email Sending

Run Django shell:
```bash
python manage.py shell
```

Test email:
```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test from LibraryMaster',
    settings.EMAIL_HOST_USER,
    ['recipient@example.com'],
)
```

## What Triggers Emails

| Event | Email Sent | How to Test |
|-------|-----------|-----------|
| Student registers | Welcome email | Create account at `/register/` |
| Create librarian | Librarian welcome | `python manage.py create_librarian lib1 email@test.com pass123` |
| Issue a book | Confirmation email | Issue a book in the app |
| Return a book | Confirmation email | Return a book in the app |
| Book becomes overdue | Overdue reminder | `python manage.py send_overdue_reminders` |
| Reserve a book | Confirmation email | Reserve a book in the app |
| Reserved book available | Available notification | Return a book that was reserved |

## Email File Locations

```
LibraryMaster/
├── accounts/
│   ├── emails.py              # Account email functions
│   └── signals.py             # Auto-send on user creation
├── library/
│   ├── emails.py              # Book email functions
│   ├── signals.py             # Auto-send on book events
│   └── management/commands/
│       └── send_overdue_reminders.py
├── templates/emails/          # All email templates
│   ├── welcome.html
│   ├── book_issued.html
│   ├── book_returned.html
│   └── ... (12 templates total)
├── .env.example               # Configuration template
└── EMAIL_INTEGRATION.md       # Full documentation
```

## Common Tasks

### Test Overdue Reminders (Dry Run)
```bash
python manage.py send_overdue_reminders --dry-run
```

### Create a Librarian Account and Send Welcome Email
```bash
python manage.py create_librarian johndoe john@library.com SecurePass123!
```

### View Email Log (if using file backend)
```bash
cat ./email-logs/*.log
```

### Check Console Output (if using console backend)
```
# Email backend logs all emails to console
# Run: python manage.py runserver
# Then create an account - you'll see the email in the terminal
```

## For Production

See [EMAIL_INTEGRATION.md](EMAIL_INTEGRATION.md) for production setup including:
- SendGrid setup
- AWS SES configuration
- Custom SMTP servers
- Rate limiting and async task queues
- Email logging and monitoring

## Troubleshooting

### Email not sending?
1. Check EMAIL_BACKEND in your `.env` file
2. Try console backend first: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
3. Check email credentials are correct
4. See EMAIL_INTEGRATION.md for detailed troubleshooting

### Gmail auth failed?
- Ensure 2-Step Verification is enabled
- Use App Password, not regular Gmail password
- Check EMAIL_HOST_USER matches your Gmail address

### Template not found?
- Templates are in `templates/emails/`
- Check file names match exactly
- Restart Django development server

## Documentation

Full documentation available in:
- **[EMAIL_INTEGRATION.md](EMAIL_INTEGRATION.md)** - Complete setup and usage guide
- **[.env.example](.env.example)** - Configuration template
- **Source code comments** - Detailed explanations in each file

## Key Files to Customize

1. **Email Templates** (templates/emails/*.html)
   - Add your library logo
   - Customize colors and branding
   - Modify email text

2. **Email Functions** (accounts/emails.py, library/emails.py)
   - Add new email types
   - Customize email content
   - Add CC/BCC recipients

3. **Management Commands** (library/management/commands/)
   - Modify reminder logic
   - Add new batch operations

## Need Help?

1. Check [EMAIL_INTEGRATION.md](EMAIL_INTEGRATION.md) for detailed guidance
2. Review code comments in email modules
3. Check Django email documentation: https://docs.djangoproject.com/en/5.2/topics/email/
4. Test using console backend first

---

**Email integration is now ready!** 🎉

Start with the console backend to test without credentials, then configure Gmail or your preferred SMTP provider.
