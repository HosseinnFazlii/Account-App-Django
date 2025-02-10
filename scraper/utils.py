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

    url = str(url)  # Convert URL object to string if needed

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = url.split("?")[0].split("/")[-1]  # Extract filename
            file_path = os.path.join(folder, filename)

            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure directory exists

            with open(full_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            return file_path  # ✅ Return the saved file path
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")

    return None


def scrape_instagram_posts(store_id, post_count=10):
    """Scrape Instagram posts and save images/videos to Django storage."""
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
            is_reel = post.media_type == 2  # ✅ Media type 2 = Video (Reel)
            cover_image_path = download_file(str(getattr(post, "thumbnail_url", "")), folder="scraper/covers/")
            image_paths = []
            video_path = None

            if is_reel:
                # ✅ Handle Reels
                video_path = download_file(str(getattr(post, "video_url", "")), folder="scraper/videos/")
            else:
                # ✅ Handle Image Posts (Single & Carousel)
                if hasattr(post, "resources") and post.resources:
                    # ✅ Multi-image carousel (loop through all images)
                    for resource in post.resources:
                        image_url = str(
                            getattr(resource, "display_url", None) or getattr(resource, "thumbnail_url", None)
                        )
                        if image_url:
                            saved_path = download_file(image_url, folder="scraper/posts/")
                            if saved_path:
                                image_paths.append(saved_path)
                else:
                    # ✅ Single-image post (use `display_url` or `thumbnail_url`)
                    single_image_url = str(getattr(post, "display_url", None) or getattr(post, "thumbnail_url", None))
                    if single_image_url:
                        saved_path = download_file(single_image_url, folder="scraper/posts/")
                        if saved_path:
                            image_paths.append(saved_path)

            # ✅ Save post in the database
            ScrapedPost.objects.update_or_create(
                post_id=str(post.id),
                store=store,
                defaults={
                    "caption": post.caption_text,
                    "cover_image": cover_image_path,
                    "images": image_paths,  # ✅ Ensure images are saved correctly
                    "video": video_path,  # ✅ Save Reel video file if it's a Reel
                    "is_reel": is_reel,
                },
            )

        return {"message": f"Scraped {len(posts)} posts for {store.name}"}

    except SellerStore.DoesNotExist:
        return {"error": "Store not found"}
    except Exception as e:
        return {"error": str(e)}
