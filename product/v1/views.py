from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Product, ShoppingCart, Category
from wallet.models import Invoice
from .serializers import ProductSerializer, ShoppingCartSerializer, CategorySerializer, InvoiceSerializer
from sellers.models import SellerStore
from wallet.models import Wallet


class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Allow sellers to create a new product."""
        try:
            seller = SellerStore.objects.get(user=request.user)
            data = request.data.copy()
            data['seller'] = seller.id
            serializer = ProductSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SellerStore.DoesNotExist:
            return Response(
                {"error": "You do not own a store."},
                status=status.HTTP_403_FORBIDDEN,
            )

class ProductListView(APIView):
    def get(self, request):
        """Retrieve the list of products."""
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """View items in the shopping cart."""
        cart_items = ShoppingCart.objects.filter(user=request.user)
        serializer = ShoppingCartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Add a product to the shopping cart."""
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
            return Response(
                {"error": "Item not found in your cart."},
                status=status.HTTP_404_NOT_FOUND,
            )

class CreateInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Generate an invoice based on the shopping cart."""
        cart_items = ShoppingCart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {"error": "Your shopping cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_amount = sum(item.total_price for item in cart_items)
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        if wallet.balance < total_amount:
            return Response(
                {"error": "Insufficient wallet balance."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice = Invoice.objects.create(
            wallet=wallet, amount=total_amount, status='unpaid'
        )

        # Clear the cart
        cart_items.delete()

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CategoryListView(APIView):
    def get(self, request):
        """Retrieve the list of categories."""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
