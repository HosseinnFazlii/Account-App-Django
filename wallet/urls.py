# financial/urls.py
from django.urls import path, include

urlpatterns = [
    path('v1/', include('financial.v1.urls')),  # Include version 1 URLs
]
