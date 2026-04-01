from django.contrib import admin
from .models import Book, IssueBook, Reservation

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'quantity']
    search_fields = ['title', 'author']

@admin.register(IssueBook)
class IssueBookAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'issue_date', 'due_date', 'return_date', 'fine']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'reserved_at']
