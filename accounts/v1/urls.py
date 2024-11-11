from django.urls import path
from .views import (
    OTPVerificationView, OTPVerifyView,
    PasswordLoginView, UserUpdateView, UserInfoView, CustomTokenRefreshView
)

urlpatterns = [
    path('verify-phone/', OTPVerificationView.as_view(), name='verify_phone'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify_otp'),
    path('login/', PasswordLoginView.as_view(), name='login'),
    path('update-user/', UserUpdateView.as_view(), name='update_user'),
    path('user-info/', UserInfoView.as_view(), name='user_info'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
