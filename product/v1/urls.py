from django.urls import path
from .views import (
    ProductCreateView, ProductListView, ProductVariantListView, ShoppingCartView,
    CreateInvoiceView, CategoryListView, AttributeListView
)

urlpatterns = [
    path('products/', ProductCreateView.as_view(), name='product_create'),
    path('products/list/', ProductListView.as_view(), name='product_list'),
    path('variants/', ProductVariantListView.as_view(), name='product_variant_list'),
    path('cart/', ShoppingCartView.as_view(), name='shopping_cart'),
    path('cart/invoice/', CreateInvoiceView.as_view(), name='create_invoice'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('attributes/', AttributeListView.as_view(), name='product_attributes'),
]
