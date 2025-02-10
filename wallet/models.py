from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta

User = get_user_model()

def default_due_date():
    """
    Returns the current time plus one day.
    """
    return now() + timedelta(days=1)

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='IRR')  # Iranian Rial

    def __str__(self):
        return f"{self.user.username}'s wallet - Balance: {self.balance}"

class Invoice(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=default_due_date)
    status = models.CharField(
        max_length=20,
        choices=[
            ('unpaid', 'Unpaid'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),  # Added "failed" status for better error handling
            ('pending', 'Pending'),  # Added "pending" to track processing payments
        ],
        default='unpaid'
    )
    is_wallet_top_up = models.BooleanField(default=False)  # ✅ New field to track top-up invoices

    def __str__(self):
        return f"Invoice {self.id} - Amount: {self.amount} - Status: {self.status} - Top-up: {self.is_wallet_top_up}"

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=[('credit', 'Credit')])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed')
    ], default='pending')
    description = models.TextField(blank=True)
    authority = models.CharField(max_length=255, blank=True, null=True)  # ZarinPal authority code

    def __str__(self):
        return f"Transaction {self.id} - {self.transaction_type} - Amount: {self.amount}"
