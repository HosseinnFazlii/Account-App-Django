from django.urls import path
from .views import (
    ProductCreateView,
    ProductListView,
    ShoppingCartView,
    CreateInvoiceView,
    CategoryListView,
)

urlpatterns = [
    path('products/', ProductCreateView.as_view(), name='product_create'),  # Endpoint for creating a product
    path('products/list/', ProductListView.as_view(), name='product_list'),  # Endpoint for listing products
    path('cart/', ShoppingCartView.as_view(), name='shopping_cart'),  # Endpoint for managing the shopping cart (GET, POST, DELETE)
    path('cart/invoice/', CreateInvoiceView.as_view(), name='create_invoice'),  # Endpoint for creating an invoice
    path('categories/', CategoryListView.as_view(), name='category_list'),  # Endpoint for listing categories
]
