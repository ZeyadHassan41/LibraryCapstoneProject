from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, CheckoutView, ReturnView, MyTransactionsView, UserListView, UserDetailView

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
    path('transactions/checkout/', CheckoutView.as_view(), name='checkout'),
    path('transactions/return/', ReturnView.as_view(), name='return'),
    path('transactions/history/', MyTransactionsView.as_view(), name='my-transactions'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
