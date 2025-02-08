import os
import requests
from django.conf import settings
from instagrapi import Client
from sellers.models import SellerStore
from scraper.models import ScrapedPost


def download_file(url, folder="scraper/media/"):
    """Download an image or video and save it to the media directory."""
    if not url or url == "None":
        return None

    url = str(url)  # Convert Pydantic URL object to string

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename = url.split("?")[0].split("/")[-1]  # Extract filename
        file_path = os.path.join(folder, filename)

        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure directory exists

        with open(full_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        return file_path  # Return file path for saving in the model
    return None


def scrape_instagram_posts(store_id, post_count=10):
    """Scrape Instagram posts and Reels and save images/videos to Django storage."""
    try:
        store = SellerStore.objects.get(id=store_id)
        username = store.instagram_id

        if not username:
            return {"error": "Instagram ID not set for this store"}

        client = Client()
        client.login(settings.INSTAGRAM_USERNAME, settings.INSTAGRAM_PASSWORD)

        user_id = client.user_id_from_username(username)
        posts = client.user_medias(user_id, post_count)

        for post in posts:
            is_reel = post.media_type == 2  # Media type 2 = Video (Reel)

            # **For Reels**
            if is_reel:
                video_path = download_file(str(getattr(post, "video_url", "")), folder="scraper/videos/")
                cover_image_path = download_file(str(getattr(post, "thumbnail_url", "")), folder="scraper/covers/")
                image_paths = []  # Reels usually don’t have multiple images

            # **For Image Posts or Carousels**
            else:
                video_path = None
                cover_image_path = download_file(str(getattr(post, "thumbnail_url", "")), folder="scraper/covers/")
                
                # 🔹 **Fix: Get exact images instead of URLs**
                image_paths = []
                for resource in post.resources:
                    image_url = str(getattr(resource, "display_url", ""))
                    if image_url:
                        image_paths.append(download_file(image_url, folder="scraper/posts/"))

            # **Save post to the database**
            ScrapedPost.objects.update_or_create(
                post_id=str(post.id),
                store=store,
                defaults={
                    "caption": post.caption_text,
                    "cover_image": cover_image_path,  # Save cover image file
                    "images": image_paths,  # Save list of images
                    "video": video_path,  # Save Reel video file if it's a Reel
                    "is_reel": is_reel,  # Flag to mark if it's a Reel
                },
            )

        return {"message": f"Scraped {len(posts)} posts for {store.name}"}

    except SellerStore.DoesNotExist:
        return {"error": "Store not found"}
    except Exception as e:
        return {"error": str(e)}
