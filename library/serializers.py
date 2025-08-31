from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Transaction

# User serializer (for listing / basic profile)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_active']

# Book serializer
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'copies_available', 'created_at', 'updated_at']

# Transaction serializer (history)
class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(write_only=True, source='book', queryset=Book.objects.all())

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'book', 'book_id', 'checkout_date', 'return_date']
        read_only_fields = ['id', 'user', 'checkout_date', 'book']
