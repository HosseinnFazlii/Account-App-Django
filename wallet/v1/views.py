from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from wallet.models import Wallet, Invoice, Transaction
from wallet.v1.serializers import WalletSerializer, InvoiceSerializer, TransactionSerializer
from zarinpal.api import ZarinPalPayment
from django.conf import settings

class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)

class InvoiceCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        data = request.data.copy()  # Copy the data to prevent mutation
        data['wallet'] = wallet.id  # Automatically associate wallet
        serializer = InvoiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(wallet=wallet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionInitiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        try:
            invoice = Invoice.objects.get(id=invoice_id, wallet__user=request.user, status='unpaid')
        except Invoice.DoesNotExist:
            return Response({"error": "Invalid or already paid invoice."}, status=status.HTTP_400_BAD_REQUEST)

        zarinpal = ZarinPalPayment(settings.ZARINPAL['MERCHANT_ID'], int(invoice.amount))
        callback_url = settings.ZARINPAL['CALLBACK_URL']
        payment_data = zarinpal.request_payment(callback_url, "Invoice Payment")

        if payment_data['success']:
            transaction = Transaction.objects.create(
                wallet=invoice.wallet,
                invoice=invoice,
                transaction_type='credit',
                amount=invoice.amount,
                status='pending',
                authority=payment_data['data']['authority']
            )
            return Response(payment_data['data'], status=status.HTTP_200_OK)
        return Response({"error": payment_data['error']}, status=status.HTTP_400_BAD_REQUEST)

class PaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        authority = request.query_params.get('Authority')
        status = request.query_params.get('Status')

        if not authority:
            return Response({"error": "Authority is required."}, status=status.HTTP_400_BAD_REQUEST)

        if status != "OK":
            # Handle NOK (failed or canceled transactions)
            return Response({"error": "Payment was not successful. Status: NOK"}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with verification for successful payments
        try:
            transaction = Transaction.objects.get(authority=authority, wallet__user=request.user, status='pending')
        except Transaction.DoesNotExist:
            return Response({"error": "Invalid or already processed transaction."}, status=status.HTTP_400_BAD_REQUEST)

        zarinpal = ZarinPalPayment(settings.ZARINPAL['MERCHANT_ID'], transaction.amount)
        verify_data = zarinpal.verify_payment(authority)

        if verify_data['success']:
            transaction.status = 'successful'
            transaction.save()

            # Update the invoice and wallet
            transaction.invoice.status = 'paid'
            transaction.invoice.save()
            transaction.wallet.balance += transaction.amount
            transaction.wallet.save()

            return Response({"message": "Payment successful."}, status=status.HTTP_200_OK)

        else:
            transaction.status = 'failed'
            transaction.save()

            return Response({"error": verify_data['error']}, status=status.HTTP_400_BAD_REQUEST)
