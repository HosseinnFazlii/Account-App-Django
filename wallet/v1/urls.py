from django.urls import path
from .views import WalletDetailView, InvoiceCreateView, TransactionInitiateView, PaymentVerifyView

urlpatterns = [
    path('wallet/', WalletDetailView.as_view(), name='wallet_detail'),
    path('invoice/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('transaction/initiate/<int:invoice_id>/', TransactionInitiateView.as_view(), name='transaction_initiate'),
    path('transaction/verify/', PaymentVerifyView.as_view(), name='payment_verify'),
]
