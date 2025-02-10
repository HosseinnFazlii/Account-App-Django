import json
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from scraper.models import ScrapedPost
from ..models import AIProcessedProduct
from .serializers import AIProcessedProductSerializer

# ✅ AI Model Endpoint
AI_API_URL = "http://host.docker.internal:11434/api/generate"
PRODUCT_REGISTRATION_URL = "http://127.0.0.1:8000/api/product/v1/products/"


class ProcessCaptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Process a caption using AI and register the product."""
        post_id = request.data.get("post_id")

        # ✅ Validate input
        try:
            scraped_post = ScrapedPost.objects.get(post_id=post_id)
        except ScrapedPost.DoesNotExist:
            return Response({"error": "Scraped post not found"}, status=status.HTTP_404_NOT_FOUND)

        caption = scraped_post.caption
        if not caption:
            return Response({"error": "Caption is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Define AI prompt
        prompt = f"""
        Extract product details from this caption and return a structured JSON response.
        Ensure:
        - "name" is the product name.
        - "description" is a short summary.
        - "category" is an integer ID.
        - "seller" is an integer ID (use 1 if unknown).
        - "variants" contains multiple options with "price", "stock", and attributes.
        - Attributes should include relevant fields such as color, size, brand.

        Caption:
        {caption}

        Expected JSON format:
        {{
            "name": "Product Name",
            "description": "Product Description",
            "category": 2,
            "seller": 1,
            "variants": [
                {{
                    "price": 20.99,
                    "stock": 100,
                    "attributes": [
                        {{"attribute": "Color", "value": "Red"}},
                        {{"attribute": "Size", "value": "L"}}
                    ]
                }}
            ]
        }}
        ONLY return valid JSON.
        """

        # ✅ Send request to AI Model
        ai_response = requests.post(AI_API_URL, json={"model": "deepseek-r1:8b", "prompt": prompt, "stream": False})

        # ✅ Handle AI errors
        if ai_response.status_code != 200:
            return Response({"error": "AI processing failed", "details": ai_response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            ai_data = ai_response.json().get("response", "{}")
            structured_data = json.loads(ai_data)  # ✅ Safely parse JSON (instead of `eval()`)
        except json.JSONDecodeError:
            return Response({"error": "AI returned invalid JSON"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ✅ Store AI-processed product
        processed_product = AIProcessedProduct.objects.create(
            scraped_post=scraped_post,
            product_data=structured_data
        )

        # ✅ Register Product
        product_response = requests.post(
            PRODUCT_REGISTRATION_URL,
            json=structured_data,
            headers={"Authorization": f"Bearer {request.auth}"}  # Use request auth token
        )

        if product_response.status_code == 201:
            return Response({
                "message": "Product registered successfully",
                "processed_data": structured_data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "error": "Product registration failed",
                "ai_data": structured_data,
                "product_api_response": product_response.json()
            }, status=status.HTTP_400_BAD_REQUEST)
