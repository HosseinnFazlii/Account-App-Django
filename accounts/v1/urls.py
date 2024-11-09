from django.urls import path
from .views import OTPVerificationView, RegisterUserView, PasswordLoginView, OTPLoginView

urlpatterns = [
    path('verify-phone/', OTPVerificationView.as_view(), name='verify_phone'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', PasswordLoginView.as_view(), name='login'),
    path('login-otp/', OTPLoginView.as_view(), name='login_otp'),
]
