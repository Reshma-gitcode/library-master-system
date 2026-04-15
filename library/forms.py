"""
library/forms.py - Forms for book management

Provides form validation for adding and editing books.
"""

from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    """
    Form for creating and editing books.

    Validates:
      - Title and author are not empty
      - Quantity is non-negative
      - ISBN (if provided) is 10 or 13 digits
    """

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'quantity']
        widgets = {
            'title':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book title'}),
            'author':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author name'}),
            'isbn':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN (optional)'}),
            'genre':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Genre'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        return title

    def clean_author(self):
        author = self.cleaned_data.get('author', '').strip()
        if not author:
            raise forms.ValidationError("Author cannot be empty.")
        return author

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty is None or qty < 0:
            raise forms.ValidationError("Quantity must be 0 or more.")
        return qty

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if not isbn:
            return isbn   
        isbn = isbn.strip()
        if len(isbn) not in [10, 13]:
            raise forms.ValidationError("ISBN must be 10 or 13 digits")
        return isbn
