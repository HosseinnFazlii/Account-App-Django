from django.urls import path
from .views import (
    SellerStoreRegisterView,
    SellerStoreUpdateView,
    #SellerStorePartialUpdateView,
    CategoryListView,
    StateCityListView,
)

urlpatterns = [
    path('register/', SellerStoreRegisterView.as_view(), name='seller_store_register'),
    path('update/', SellerStoreUpdateView.as_view(), name='seller_store_update'),
    #path('update-partial/', SellerStorePartialUpdateView.as_view(), name='seller_store_partial_update'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('state-city/', StateCityListView.as_view(), name='state_city_list'),
]
