from django.db import models
from scraper.models import ScrapedPost
from sellers.models import SellerStore

class AIProcessedProduct(models.Model):
    scraped_post = models.OneToOneField(ScrapedPost, on_delete=models.CASCADE, related_name="ai_processed")
    product_data = models.JSONField()  # Store the structured AI response
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Processed: {self.scraped_post.post_id}"
