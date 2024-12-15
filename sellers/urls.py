from django.urls import include, path

urlpatterns = [
    path('v1/', include('sellers.v1.urls')),  # Include version 1 URLs
]
