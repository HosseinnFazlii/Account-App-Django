from rest_framework import serializers
from wallet.models import Wallet, Invoice, Transaction

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'currency']  # Removed 'user' to avoid exposing user details

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'amount', 'created_at', 'due_date', 'status']
        read_only_fields = ['created_at', 'due_date', 'status', 'wallet']  # Ensure wallet is not user-editable

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'wallet', 'invoice', 'transaction_type', 'amount',
            'created_at', 'status', 'description', 'authority'
        ]
        read_only_fields = ['created_at', 'status', 'authority', 'wallet', 'invoice']  # Prevent wallet and invoice edits
