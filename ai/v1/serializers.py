from rest_framework import serializers
from ..models import AIProcessedProduct

class AIProcessedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIProcessedProduct
        fields = '__all__'
