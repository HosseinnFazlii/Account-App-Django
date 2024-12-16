from django.contrib import admin
from .models import Wallet, Invoice, Transaction

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'currency')
    search_fields = ('user__phone_number', 'currency')
    list_filter = ('currency',)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'amount', 'status', 'created_at', 'due_date')
    list_filter = ('status',)
    search_fields = ('wallet__user__phone_number',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')
    search_fields = ('wallet__user__phone_number', 'description', 'authority')

admin.site.register(Wallet, WalletAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Transaction, TransactionAdmin)
