# financial/serializers.py

from rest_framework import serializers
from ..models import Invoice, Transaction

class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['amount', 'due_date']

class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['invoice', 'amount', 'description']
