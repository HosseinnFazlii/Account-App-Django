# financial/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from ..models import Wallet, Invoice, Transaction
from .serializers import InvoiceCreateSerializer
from zarinpal.api import ZarinPalPayment

class InvoiceCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InvoiceCreateSerializer(data=request.data)
        if serializer.is_valid():
            wallet = Wallet.objects.get(user=request.user)
            invoice = serializer.save(wallet=wallet)
            return Response({
                "message": "Invoice created successfully",
                "invoice_id": invoice.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id, wallet__user=request.user, status='unpaid')
        zarinpal = ZarinPalPayment(settings.ZARINPAL['MERCHANT_ID'], invoice.amount)
        result = zarinpal.request_payment(
            settings.ZARINPAL['CALLBACK_URL'],
            description=f'Payment for Invoice {invoice.id}',
            email=request.user.email,
            mobile=request.user.profile.phone_number  # Assuming a profile model with phone_number
        )
        if result['Status'] == 100:
            transaction = Transaction.objects.create(
                wallet=invoice.wallet,
                invoice=invoice,
                transaction_type='credit',
                amount=invoice.amount,
                status='pending',
                description='Payment for invoice',
                authority=result['Authority']
            )
            payment_url = zarinpal.get_payment_url(result['Authority'])
            return Response({
                "message": "Transaction initiated successfully",
                "transaction_id": transaction.id,
                "payment_url": payment_url
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Failed to initiate payment."}, status=status.HTTP_400_BAD_REQUEST)

class PaymentVerifyView(APIView):
    def get(self, request):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        transaction = get_object_or_404(Transaction, authority=authority)
        if status == 'OK':
            zarinpal = ZarinPalPayment(settings.ZARINPAL['MERCHANT_ID'], transaction.amount)
            result = zarinpal.verify_payment(authority)
            if result['Status'] == 100:
                transaction.status = 'successful'
                transaction.save()
                invoice = transaction.invoice
                invoice.status = 'paid'
                invoice.save()
                wallet = invoice.wallet
                wallet.balance += transaction.amount
                wallet.save()
                return Response({"message": "Payment successful, wallet balance updated."}, status=status.HTTP_200_OK)
            else:
                transaction.status = 'failed'
                transaction.save()
                return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            transaction.status = 'failed'
            transaction.save()
            return Response({"error": "Payment was not successful."}, status=status.HTTP_400_BAD_REQUEST)
