from django.urls import path
from .views import ProcessCaptionView

urlpatterns = [
    path('process/', ProcessCaptionView.as_view(), name='process_caption'),
]
