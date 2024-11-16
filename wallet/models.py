# financial/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='IRR')  # Iranian Rial

    def __str__(self):
        return f"{self.user.username}'s wallet - Balance: {self.balance}"

class Invoice(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ], default='unpaid')

    def __str__(self):
        return f"Invoice {self.id} - Amount: {self.amount} - Status: {self.status}"

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
