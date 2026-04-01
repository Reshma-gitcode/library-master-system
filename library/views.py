from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db import transaction
from django.db.models import Count
from datetime import date

from .models import Book, IssueBook, Reservation
from .forms import BookForm


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


# ─── BOOK LIST ───────────────────────────────────────────────────────────────
@login_required
def book_list(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.all().order_by('title')

    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)

    # Attach user's active issues so template knows what they have
    user_issued_ids = set(
        IssueBook.objects.filter(user=request.user, return_date=None)
        .values_list('book_id', flat=True)
    )
    user_reserved_ids = set(
        Reservation.objects.filter(user=request.user)
        .values_list('book_id', flat=True)
    )

    paginator = Paginator(books, 9)
    page = request.GET.get('page')
    books_page = paginator.get_page(page)

    return render(request, 'library/book_list.html', {
        'books': books_page,
        'query': query,
        'user_issued_ids': user_issued_ids,
        'user_reserved_ids': user_reserved_ids,
    })


# ─── ADD BOOK (ADMIN ONLY) ────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def add_book(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Book added successfully.")
        return redirect('book_list')
    return render(request, 'library/add_book.html', {'form': form})


# ─── EDIT BOOK (ADMIN ONLY) ───────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    form = BookForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        messages.success(request, "Book updated successfully.")
        return redirect('book_list')
    return render(request, 'library/add_book.html', {'form': form, 'edit': True})


# ─── DELETE BOOK (ADMIN ONLY) ─────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, "Book deleted.")
    return redirect('book_list')


# ─── ISSUE BOOK ───────────────────────────────────────────────────────────────
@login_required
def issue_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if IssueBook.objects.filter(user=request.user, book=book, return_date=None).exists():
        messages.warning(request, "You already have this book issued.")
        return redirect('book_list')

    with transaction.atomic():
        book = Book.objects.select_for_update().get(id=book_id)
        if book.quantity <= 0:
            messages.error(request, "Book is out of stock.")
            return redirect('book_list')

        IssueBook.objects.create(user=request.user, book=book)
        book.quantity -= 1
        book.save()

    messages.success(request, f'"{book.title}" issued successfully. Due in 7 days.')
    return redirect('my_books')


# ─── RETURN BOOK ──────────────────────────────────────────────────────────────
@login_required
def return_book(request, issue_id):
    issue = get_object_or_404(IssueBook, id=issue_id, user=request.user, return_date=None)
    book = issue.book

    with transaction.atomic():
        issue.return_date = date.today()
        issue.fine = issue.calculate_fine()
        issue.save()

        book.quantity += 1
        book.save()

    if issue.fine > 0:
        send_mail(
            'Library Fine Alert',
            f'You have a fine of Rs.{issue.fine} for returning "{book.title}" late.',
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=True,
        )
        messages.warning(request, f'Book returned. Fine: Rs.{issue.fine} (overdue by {(issue.return_date - issue.due_date).days} days).')
    else:
        messages.success(request, "Book returned successfully.")

    # Auto-issue to first reservation
    reservation = Reservation.objects.filter(book=book).order_by('reserved_at').first()
    if reservation:
        with transaction.atomic():
            b = Book.objects.select_for_update().get(id=book.id)
            if b.quantity > 0:
                IssueBook.objects.create(user=reservation.user, book=b)
                b.quantity -= 1
                b.save()
                reservation.delete()
                send_mail(
                    'Reserved Book Now Issued',
                    f'Your reserved book "{b.title}" has been issued to you.',
                    settings.EMAIL_HOST_USER,
                    [reservation.user.email],
                    fail_silently=True,
                )

    return redirect('my_books')


# ─── RESERVE BOOK ─────────────────────────────────────────────────────────────
@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if IssueBook.objects.filter(user=request.user, book=book, return_date=None).exists():
        messages.warning(request, "You already have this book issued.")
        return redirect('book_list')

    if book.quantity > 0:
        messages.info(request, "This book is available — you can issue it directly.")
        return redirect('book_list')

    if Reservation.objects.filter(user=request.user, book=book).exists():
        messages.warning(request, "You already have a reservation for this book.")
        return redirect('book_list')

    Reservation.objects.create(user=request.user, book=book)
    send_mail(
        'Book Reserved',
        f'You have reserved "{book.title}". We will notify you when it becomes available.',
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=True,
    )
    messages.success(request, f'"{book.title}" reserved. You will be notified when available.')
    return redirect('my_reservations')


# ─── CANCEL RESERVATION ───────────────────────────────────────────────────────
@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Reservation cancelled.")
    return redirect('my_reservations')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    today = date.today()
    overdue = IssueBook.objects.filter(return_date=None, due_date__lt=today)

    context = {
        'total_books': Book.objects.count(),
        'issued_books': IssueBook.objects.filter(return_date=None).count(),
        'total_fine': sum(i.fine for i in IssueBook.objects.exclude(fine=0)),
        'overdue_count': overdue.count(),
        'top_books': Book.objects.annotate(total=Count('issuebook_set')).order_by('-total')[:5],
    }

    if is_admin(request.user):
        context['overdue_issues'] = overdue.select_related('user', 'book')[:10]
        context['pending_fines'] = IssueBook.objects.filter(fine__gt=0, fine_paid=False).select_related('user', 'book')[:10]

    return render(request, 'library/dashboard.html', context)


# ─── MARK FINE AS PAID (ADMIN ONLY) ──────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def mark_fine_paid(request, issue_id):
    issue = get_object_or_404(IssueBook, id=issue_id)
    if request.method == 'POST':
        issue.fine_paid = True
        issue.save()
        messages.success(request, f'Fine for "{issue.book.title}" marked as paid.')
    return redirect('dashboard')
@login_required
def my_books(request):
    if is_admin(request.user):
        active = IssueBook.objects.filter(return_date=None).select_related('user', 'book').order_by('due_date')
        history = IssueBook.objects.exclude(return_date=None).select_related('user', 'book').order_by('-return_date')
    else:
        active = IssueBook.objects.filter(user=request.user, return_date=None).select_related('book')
        history = IssueBook.objects.filter(user=request.user).exclude(return_date=None).select_related('book').order_by('-return_date')
    return render(request, 'library/my_books.html', {'active': active, 'history': history})


# ─── MY RESERVATIONS ──────────────────────────────────────────────────────────
@login_required
def my_reservations(request):
    if is_admin(request.user):
        res = Reservation.objects.all().select_related('user', 'book').order_by('reserved_at')
    else:
        res = Reservation.objects.filter(user=request.user).select_related('book')
    return render(request, 'library/my_reservations.html', {'res': res})
