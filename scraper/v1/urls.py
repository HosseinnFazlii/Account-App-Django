from django.urls import path
from scraper.v1.views import ScrapePostsView

urlpatterns = [
    path("scrape/", ScrapePostsView.as_view(), name="scrape_posts"),
]
