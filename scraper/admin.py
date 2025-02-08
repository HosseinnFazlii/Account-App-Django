from django.utils.html import format_html
from django.contrib import admin
from scraper.models import ScrapedPost

class ScrapedPostAdmin(admin.ModelAdmin):
    list_display = ("store", "post_id", "caption", "is_reel", "is_ai_read", "created_at", "image_tag", "video_tag")
    list_filter = ("is_reel", "is_ai_read", "store")
    search_fields = ("post_id", "caption", "store__name")
    ordering = ("-created_at",)

    def image_tag(self, obj):
        """Display the cover image in Django Admin."""
        if obj.cover_image:  # Ensure the field is not empty
            return format_html(f'<img src="/media/{obj.cover_image}" width="100" style="border-radius:8px;" />')
        return "No Cover"

    def video_tag(self, obj):
        """Display the video in Django Admin."""
        if obj.video:  # Ensure the field is not empty
            return format_html(f'<video width="100" controls><source src="/media/{obj.video}" type="video/mp4"></video>')
        return "No Video"

    image_tag.short_description = "Cover Image"
    video_tag.short_description = "Video"

admin.site.register(ScrapedPost, ScrapedPostAdmin)
