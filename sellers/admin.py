from django.contrib import admin
from .models import SellerStore, Category, State, City

class SellerStoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'category', 'state', 'city', 'created_at')
    search_fields = ('name', 'phone', 'user__phone_number')
    list_filter = ('category', 'state', 'city')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    search_fields = ('name', 'state__name')
    list_filter = ('state',)

admin.site.register(SellerStore, SellerStoreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
