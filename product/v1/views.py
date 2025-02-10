from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import (
    Product, ShoppingCart, Category,
    Attribute, AttributeValue, ProductAttribute, ProductVariant
)
from wallet.models import Invoice
from .serializers import (
    ProductSerializer, ShoppingCartSerializer, CategorySerializer, InvoiceSerializer,
    AttributeSerializer, AttributeValueSerializer, ProductVariantSerializer
)
from sellers.models import SellerStore
from wallet.models import Wallet
from django.conf import settings
import requests

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Allow sellers to create a new product with variants."""
        try:
            seller = SellerStore.objects.get(user=request.user)
            data = request.data.copy()
            data['seller'] = seller.id
            variants_data = data.pop('variants', [])

            serializer = ProductSerializer(data=data)

            if serializer.is_valid():
                product = serializer.save()

                # Process product variants
                variant_objects = []
                for variant_data in variants_data:
                    price = variant_data.get("price")
                    stock = variant_data.get("stock")
                    attribute_values = variant_data.get("attributes", [])

                    attribute_value_objects = []
                    for attr_value in attribute_values:
                        attribute_name = attr_value.get("attribute")
                        value_name = attr_value.get("value")

                        attribute, _ = Attribute.objects.get_or_create(name=attribute_name)
                        attribute.categories.add(product.category)

                        attribute_value, _ = AttributeValue.objects.get_or_create(
                            attribute=attribute, value=value_name
                        )
                        product_attribute, _ = ProductAttribute.objects.get_or_create(
                            product=product, attribute=attribute, value=attribute_value
                        )
                        attribute_value_objects.append(product_attribute)

                    variant = ProductVariant.objects.create(product=product, price=price, stock=stock)
                    variant.attributes.set(attribute_value_objects)
                    variant_objects.append(variant)

                return Response({
                    "product": ProductSerializer(product).data,
                    "variants": ProductVariantSerializer(variant_objects, many=True).data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SellerStore.DoesNotExist:
            return Response({"error": "You do not own a store."}, status=status.HTTP_403_FORBIDDEN)


class ProductListView(APIView):
    def get(self, request):
        """Retrieve the list of products."""
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductVariantListView(APIView):
    def get(self, request):
        """Retrieve the list of product variants."""
        variants = ProductVariant.objects.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AttributeListView(APIView):
    def get(self, request):
        """Retrieve the list of product attributes (e.g., Color, Size)."""
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """View items in the shopping cart."""
        cart_items = ShoppingCart.objects.filter(user=request.user)
        serializer = ShoppingCartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Add a product variant to the shopping cart."""
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ShoppingCartSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Remove an item from the shopping cart."""
        try:
            item_id = request.data.get('id')
            cart_item = ShoppingCart.objects.get(id=item_id, user=request.user)
            cart_item.delete()
            return Response({"message": "Item removed from cart."}, status=status.HTTP_200_OK)
        except ShoppingCart.DoesNotExist:
            return Response({"error": "Item not found in your cart."}, status=status.HTTP_404_NOT_FOUND)


class CreateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Generate an invoice based on the shopping cart and handle insufficient balance."""
        cart_items = ShoppingCart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response({"error": "Your shopping cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = sum(item.total_price() for item in cart_items)  # Ensure this is a method call
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        if wallet.balance < total_amount:
            # ✅ Auto-create a wallet top-up invoice
            amount_needed = total_amount - wallet.balance  # Amount required to complete the purchase
            top_up_invoice = Invoice.objects.create(
                wallet=wallet,
                amount=amount_needed,
                status='pending',  # Payment is required
                is_wallet_top_up=True  # Mark as wallet top-up invoice
            )

            # ✅ Generate Zarinpal payment link
            zarinpal_request_url = "https://api.zarinpal.com/pg/v4/payment/request.json"
            callback_url = f"{settings.ZARINPAL['CALLBACK_URL']}?invoice_id={top_up_invoice.id}"
            
            data = {
                "merchant_id": settings.ZARINPAL["MERCHANT_ID"],
                "amount": int(amount_needed * 10),  # Zarinpal works with Tomans (Rial / 10)
                "callback_url": callback_url,
                "description": f"Wallet top-up for {request.user.phone_number}",
            }
            headers = {"Content-Type": "application/json"}

            response = requests.post(zarinpal_request_url, json=data, headers=headers)
            result = response.json()

            if "data" in result and "authority" in result["data"]:
                payment_url = f"https://www.zarinpal.com/pg/StartPay/{result['data']['authority']}"

                return Response({
                    "error": "Insufficient wallet balance.",
                    "message": "Redirecting to wallet top-up.",
                    "wallet_top_up_invoice_id": top_up_invoice.id,
                    "redirect_url": payment_url
                }, status=status.HTTP_402_PAYMENT_REQUIRED)  # 402 = Payment Required

            return Response({"error": "Zarinpal payment request failed.", "details": result}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Proceed with checkout if balance is enough
        invoice = Invoice.objects.create(wallet=wallet, amount=total_amount, status='unpaid')

        cart_items.delete()

        return Response({
            "message": "Invoice created successfully.",
            "invoice_id": invoice.id,
            "amount": total_amount
        }, status=status.HTTP_201_CREATED)


class CategoryListView(APIView):
    def get(self, request):
        """Retrieve the list of categories."""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
