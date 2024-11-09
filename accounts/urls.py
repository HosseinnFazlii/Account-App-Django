from django.urls import path, include

urlpatterns = [
    path('v1/', include('accounts.v1.urls')),  # Version 1 URLs
]
