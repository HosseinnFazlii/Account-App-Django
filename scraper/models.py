from django.db import models
from sellers.models import SellerStore

class ScrapedPost(models.Model):
    store = models.ForeignKey(SellerStore, on_delete=models.CASCADE, related_name="scraped_posts")
    post_id = models.CharField(max_length=100, unique=True)  # Instagram post ID
    caption = models.TextField(blank=True, null=True)
    cover_image = models.CharField(max_length=255, blank=True, null=True)  # Local file path
    images = models.JSONField(default=list)  # List of local image file paths
    video = models.CharField(max_length=255, blank=True, null=True)  # Local video file path
    is_reel = models.BooleanField(default=False)  # True if it's a Reel
    is_ai_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.store.name} - {self.post_id}"
