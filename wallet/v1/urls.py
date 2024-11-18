# financial/v1/urls.py
from django.urls import path
from .views import InvoiceCreateView, TransactionInitiateView, PaymentVerifyView

urlpatterns = [
    path('invoice/create/', InvoiceCreateView.as_view(), name='create_invoice'),
    path('transaction/initiate/<int:invoice_id>/', TransactionInitiateView.as_view(), name='initiate_transaction'),
    path('transaction/verify/', PaymentVerifyView.as_view(), name='verify_payment'),
]
