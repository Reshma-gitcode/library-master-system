"""
library/urls.py - URL routing for the library app

Maps URLs to view functions for all book-related operations.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Catalogue
    path('',                                    views.book_list,          name='book_list'),
    path('add/',                                views.add_book,           name='add_book'),
    path('edit/<int:book_id>/',                 views.edit_book,          name='edit_book'),
    path('delete/<int:book_id>/',               views.delete_book,        name='delete_book'),

    # Issue & Return
    path('issue/<int:book_id>/',                views.issue_book,         name='issue_book'),
    path('return/<int:issue_id>/',              views.return_book,        name='return_book'),

    # Reservations
    path('reserve/<int:book_id>/',              views.reserve_book,       name='reserve_book'),
    path('reservation/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),

    # Dashboard & Reports
    path('dashboard/',                          views.dashboard,          name='dashboard'),
    path('my-books/',                           views.my_books,           name='my_books'),
    path('my-reservations/',                    views.my_reservations,    name='my_reservations'),

    # Fine Management
    path('fine/paid/<int:issue_id>/',           views.mark_fine_paid,     name='mark_fine_paid'),
]
