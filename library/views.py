from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Avg
from datetime import date

from .models import Book, IssueBook, Reservation, Review, Notification
from .forms import BookForm, ReviewForm


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def _send_email(subject, body, recipient):
    send_mail(subject, body, settings.EMAIL_HOST_USER, [recipient], fail_silently=True)


@login_required
def book_list(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('genre', 'title')
    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)
    
    # Compute genre counts from filtered books
    genre_counts = books.values('genre').annotate(count=Count('id')).order_by('genre')
    genre_counts_dict = {item['genre']: item['count'] for item in genre_counts}
    
    # Group books by genre for the page
    books_page = books  # No pagination for now, as grouping changes it
    genre_groups = {}
    for book in books_page:
        genre = book.genre
        if genre not in genre_groups:
            genre_groups[genre] = []
        genre_groups[genre].append(book)
    
    user_issued_ids = set(IssueBook.objects.filter(user=request.user, return_date=None).values_list('book_id', flat=True))
    user_reserved_ids = set(Reservation.objects.filter(user=request.user).values_list('book_id', flat=True))
    
    return render(request, 'library/book_list.html', {
        'genre_groups': genre_groups,
        'genre_counts': genre_counts_dict,
        'query': query,
        'user_issued_ids': user_issued_ids,
        'user_reserved_ids': user_reserved_ids
    })


@login_required
@user_passes_test(is_admin)
def add_book(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Book added successfully.")
        return redirect('book_list')
    return render(request, 'library/add_book.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    old_quantity = book.quantity  # Track old quantity
    form = BookForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        
        # If book quantity increased from 0 to > 0, process reservations
        if old_quantity == 0 and book.quantity > 0:
            reservations = Reservation.objects.filter(book=book).order_by('reserved_at')
            for reservation in reservations[:book.quantity]:
                with transaction.atomic():
                    b = Book.objects.select_for_update().get(id=book.id)
                    if b.quantity > 0:
                        IssueBook.objects.create(user=reservation.user, book=b)
                        b.quantity -= 1
                        b.save()
                        reservation.delete()
                        _send_email('Reserved Book Now Issued', f'Your reserved book "{b.title}" has been issued to you.', reservation.user.email)
                        Notification.objects.create(
                            user=reservation.user,
                            message=f'Your reserved book "{b.title}" is now available and has been issued to you.'
                        )
        
        messages.success(request, "Book updated successfully.")
        return redirect('book_list')
    return render(request, 'library/add_book.html', {'form': form, 'edit': True})


@login_required
@user_passes_test(is_admin)
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, "Book deleted.")
    return redirect('book_list')


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


@login_required
def return_book(request, issue_id):
    issue = get_object_or_404(IssueBook, id=issue_id)
    if issue.return_date is not None:
        messages.warning(request, "This book has already been returned.")
        return redirect('my_books')
    if not is_admin(request.user) and issue.user != request.user:
        messages.error(request, "You can only return your own books.")
        return redirect('my_books')
    book = issue.book
    with transaction.atomic():
        issue.return_date = date.today()
        issue.fine = issue.calculate_fine()
        issue.save()
        book.quantity += 1
        book.save()
    if issue.fine > 0:
        days_late = (issue.return_date - issue.due_date).days
        _send_email('Library Fine Alert', f'You have a fine of Rs.{issue.fine} for returning "{book.title}" {days_late} days late.', issue.user.email)
        messages.warning(request, f'Book returned. Fine: Rs.{issue.fine} ({days_late} days overdue).')
    else:
        messages.success(request, "Book returned successfully.")
    reservation = Reservation.objects.filter(book=book).order_by('reserved_at').first()
    if reservation:
        with transaction.atomic():
            b = Book.objects.select_for_update().get(id=book.id)
            if b.quantity > 0:
                IssueBook.objects.create(user=reservation.user, book=b)
                b.quantity -= 1
                b.save()
                reservation.delete()
                _send_email('Reserved Book Now Issued', f'Your reserved book "{b.title}" has been issued to you.', reservation.user.email)
                Notification.objects.create(
                    user=reservation.user,
                    message=f'Your reserved book "{b.title}" is now available and has been issued to you.'
                )
    return redirect('my_books')


@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if IssueBook.objects.filter(user=request.user, book=book, return_date=None).exists():
        messages.warning(request, "You already have this book issued.")
        return redirect('book_list')
    if book.quantity > 0:
        messages.info(request, "This book is available - you can issue it directly.")
        return redirect('book_list')
    if Reservation.objects.filter(user=request.user, book=book).exists():
        messages.warning(request, "You already have a reservation for this book.")
        return redirect('book_list')
    Reservation.objects.create(user=request.user, book=book)
    _send_email('Book Reserved', f'You have reserved "{book.title}". We will notify you when available.', request.user.email)
    messages.success(request, f'"{book.title}" reserved.')
    return redirect('my_reservations')


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if not is_admin(request.user) and reservation.user != request.user:
        messages.error(request, "You can only cancel your own reservations.")
        return redirect('my_reservations')
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Reservation cancelled.")
    return redirect('my_reservations')


@login_required
def dashboard(request):
    today = date.today()
    overdue = IssueBook.objects.filter(return_date=None, due_date__lt=today)
    context = {
        'total_books': Book.objects.count(),
        'issued_books': IssueBook.objects.filter(return_date=None).count(),
        'total_fine': sum(i.current_fine for i in IssueBook.objects.all()),
        'overdue_count': overdue.count(),
        'top_books': Book.objects.annotate(total=Count('issuebook_set')).order_by('-total')[:5],
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
    }
    if is_admin(request.user):
        context['overdue_issues'] = overdue.select_related('user', 'book')[:10]
        context['pending_fines'] = IssueBook.objects.filter(fine__gt=0, fine_paid=False).select_related('user', 'book')[:10]
    return render(request, 'library/dashboard.html', context)


@login_required
def my_books(request):
    if is_admin(request.user):
        active = IssueBook.objects.filter(return_date=None).select_related('user', 'book').order_by('due_date')
        history = IssueBook.objects.exclude(return_date=None).select_related('user', 'book').order_by('-return_date')
    else:
        active = IssueBook.objects.filter(user=request.user, return_date=None).select_related('book')
        history = IssueBook.objects.filter(user=request.user).exclude(return_date=None).select_related('book').order_by('-return_date')
    return render(request, 'library/my_books.html', {'active': active, 'history': history})


@login_required
def my_reservations(request):
    if is_admin(request.user):
        res = Reservation.objects.all().select_related('user', 'book').order_by('reserved_at')
    else:
        res = Reservation.objects.filter(user=request.user).select_related('book')
    return render(request, 'library/my_reservations.html', {'res': res})


@login_required
def book_detail(request, book_id):
    """
    Display detailed book information, reviews, and allow eligible users to submit reviews.
    """
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book).select_related('user')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()

    # Check if user can review: student who has issued this book
    can_review = (request.user.role == 'student' and
                  IssueBook.objects.filter(user=request.user, book=book).exists())

    if request.method == 'POST' and can_review:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.get_or_create(
                user=request.user, book=book,
                defaults={'rating': form.cleaned_data['rating'], 'comment': form.cleaned_data['comment']}
            )
            if not created:
                review.rating = form.cleaned_data['rating']
                review.comment = form.cleaned_data['comment']
                review.save()
            messages.success(request, "Review submitted successfully.")
            return redirect('book_detail', book_id=book_id)
    else:
        form = ReviewForm()

    user_issued_ids = set(IssueBook.objects.filter(user=request.user, return_date=None).values_list('book_id', flat=True))
    user_reserved_ids = set(Reservation.objects.filter(user=request.user).values_list('book_id', flat=True))

    context = {
        'book': book,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'form': form if can_review else None,
        'can_review': can_review,
        'user_issued_ids': user_issued_ids,
        'user_reserved_ids': user_reserved_ids,
    }
    return render(request, 'library/book_detail.html', context)


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
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if request.method == 'POST':
        notification.is_read = True
        notification.save()
    return redirect('dashboard')
