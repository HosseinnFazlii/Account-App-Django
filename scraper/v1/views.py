from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from scraper.utils import scrape_instagram_posts  # Import the scraper function
from sellers.models import SellerStore

class ScrapePostsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Trigger Instagram post and Reels scraping for a store."""
        store_id = request.data.get("store_id")
        post_count = int(request.data.get("count", 10))  # Default to 10 posts

        if not store_id or not str(store_id).isdigit():
            return Response({"error": "Store ID must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)

        result = scrape_instagram_posts(int(store_id), post_count)  # Convert to int

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)