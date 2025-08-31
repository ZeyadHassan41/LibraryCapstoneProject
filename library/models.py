from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL  # django.contrib.auth.models.User by default

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)  # unique ISBN
    published_date = models.DateField(null=True, blank=True)
    copies_available = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} — {self.author}"

class Transaction(models.Model):
    """
    Represents a checkout and (optionally) a return.
    If return_date is null → book is currently checked out.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    checkout_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-checkout_date']

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({'returned' if self.return_date else 'out'})"
