from django.contrib import admin
from .models import (
    Category, Product, ShoppingCart, 
    Attribute, AttributeValue, ProductAttribute, ProductVariant
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('id',)
    list_per_page = 25


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_categories')
    search_fields = ('name',)
    ordering = ('id',)
    list_per_page = 25

    def get_categories(self, obj):
        """Show categories associated with the attribute."""
        return ", ".join([cat.name for cat in obj.categories.all()])
    get_categories.short_description = "Categories"


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value')
    search_fields = ('attribute__name', 'value')
    ordering = ('id',)
    list_per_page = 25


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'seller', 'category')
    search_fields = ('name', 'seller__user__phone_number', 'category__name')
    ordering = ('id',)
    list_per_page = 25
    raw_id_fields = ('seller',)


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'attribute', 'value')
    search_fields = ('product__name', 'attribute__name', 'value__value')
    ordering = ('id',)
    list_per_page = 25


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'price', 'stock', 'get_attributes')
    search_fields = ('product__name',)
    ordering = ('id',)
    list_per_page = 25

    def get_attributes(self, obj):
        """Display attributes in the list view."""
        return ", ".join([f"{attr.attribute.name}: {attr.value.value}" for attr in obj.attributes.all()])
    get_attributes.short_description = "Attributes"


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_variant', 'quantity', 'total_price')
    search_fields = ('user__username', 'product_variant__product__name')
    ordering = ('id',)
    list_per_page = 25

    def total_price(self, obj):
        return obj.quantity * obj.product_variant.price
    total_price.short_description = "Total Price"
