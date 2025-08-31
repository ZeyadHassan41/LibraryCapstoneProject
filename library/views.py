from rest_framework import viewsets, generics, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.utils import timezone

from .models import Book, Transaction
from .serializers import BookSerializer, TransactionSerializer, UserSerializer

# BookViewSet: CRUD + filtering for availability
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Book.objects.all()
        # filters: ?available=true, ?title=..., ?author=..., ?isbn=...
        avail = self.request.query_params.get('available')
        title = self.request.query_params.get('title')
        author = self.request.query_params.get('author')
        isbn = self.request.query_params.get('isbn')

        if avail is not None:
            if avail.lower() in ['1', 'true', 'yes']:
                qs = qs.filter(copies_available__gt=0)
            elif avail.lower() in ['0', 'false', 'no']:
                qs = qs.filter(copies_available__lte=0)

        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(author__icontains=author)
        if isbn:
            qs = qs.filter(isbn__icontains=isbn)

        return qs

# User views (admin can list all, users can view their own)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    # allow users to get/update their own record; admin can access any
    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.is_staff or user == obj:
            return obj
        self.permission_denied(self.request, message="You can only access your own user data.")

# Transactions: checkout / return / history
from rest_framework.views import APIView

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request, format=None):
        """
        POST payload: {"book_id": <id>}
        """
        user = request.user
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"detail": "book_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, pk=book_id)

        # ensure copies available
        if book.copies_available <= 0:
            return Response({"detail": "No copies available."}, status=status.HTTP_400_BAD_REQUEST)

        # ensure user doesn't already have an active checkout for this book
        active = Transaction.objects.filter(user=user, book=book, return_date__isnull=True).exists()
        if active:
            return Response({"detail": "You already have this book checked out."}, status=status.HTTP_400_BAD_REQUEST)

        # create transaction and decrement copies
        book.copies_available -= 1
        book.save()

        txn = Transaction.objects.create(user=user, book=book)
        serializer = TransactionSerializer(txn)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReturnView(APIView):
    permission_classes = [IsAuthenticated]

    @db_transaction.atomic
    def post(self, request, format=None):
        """
        POST payload: {"transaction_id": <id>} OR {"book_id": <id>}
        If book_id is provided we find the active transaction for the user and that book.
        """
        user = request.user
        transaction_id = request.data.get('transaction_id')
        book_id = request.data.get('book_id')

        if not transaction_id and not book_id:
            return Response({"detail": "transaction_id or book_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if transaction_id:
            txn = get_object_or_404(Transaction, pk=transaction_id, user=user)
        else:
            txn = Transaction.objects.filter(user=user, book_id=book_id, return_date__isnull=True).first()
            if not txn:
                return Response({"detail": "No active checkout found for this book by you."}, status=status.HTTP_400_BAD_REQUEST)

        if txn.return_date:
            return Response({"detail": "This transaction already returned."}, status=status.HTTP_400_BAD_REQUEST)

        # mark returned and increment copies
        txn.return_date = timezone.now()
        txn.save()

        book = txn.book
        book.copies_available += 1
        book.save()

        serializer = TransactionSerializer(txn)
        return Response(serializer.data, status=status.HTTP_200_OK)

# User transaction history
class MyTransactionsView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-checkout_date')
