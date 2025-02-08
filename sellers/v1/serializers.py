from rest_framework import serializers
from sellers.models import SellerStore, Category, State, City


class SellerStoreSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(read_only=True)  # Ensure phone is not required from input

    class Meta:
        model = SellerStore
        fields = [
            'id', 'username', 'phone', 'name', 'logo', 'category',
            'state', 'city', 'description', 'instagram_id', 'created_at'
        ]
        read_only_fields = ['username', 'phone', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'state']
