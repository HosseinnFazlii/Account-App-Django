from django.contrib import admin
from .models import Category, Product, ShoppingCart

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('id',)
    list_per_page = 25

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'seller', 'category', 'price', 'stock')
    search_fields = ('name', 'seller__user__phone_number', 'category__name')
    list_filter = ('category',)
    ordering = ('id',)
    list_per_page = 25
    raw_id_fields = ('seller',)  # Helps with performance if there are many sellers

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_price')
    search_fields = ('user__phone_number', 'product__name')
    ordering = ('id',)
    list_per_page = 25
