from django.urls import path
from .views import (
    ProductCreateView,
    ProductListView,
    ShoppingCartView,
    CreateInvoiceView,
    CategoryListView,
)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('cart/', ShoppingCartView.as_view(), name='shopping_cart'),
    path('cart/checkout/', CreateInvoiceView.as_view(), name='create_invoice'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
]
