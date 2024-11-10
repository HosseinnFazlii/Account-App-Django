from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer, LoginSerializer, OTPSerializer,
    OTPVerifySerializer, PasswordResetSerializer
)
from accounts.utils import send_verification_code
import random

User = get_user_model()

# Helper function to generate JWT tokens for a user
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# View to send OTP for phone number verification
class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = str(random.randint(1000, 9999))  # Generate a random 4-digit OTP
            
            # Attempt to send the OTP via SMS API
            success, message = send_verification_code(phone_number, otp)
            if success:
                user, created = User.objects.get_or_create(phone_number=phone_number)
                user.otp = otp
                user.otp_verified = False  # Set to unverified until OTP validation
                user.save()
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"Failed to send OTP: {message}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User registration endpoint
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.filter(phone_number=phone_number).first()
            if user and user.otp_verified:
                serializer.save()
                return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Phone number not verified."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Password-based login
class PasswordLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            user = authenticate(phone_number=phone_number, password=password)
            if user:
                tokens = get_tokens_for_user(user)
                return Response(tokens, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OTP-based login
class OTPLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.filter(phone_number=phone_number, otp_verified=True).first()
            if user:
                otp = str(random.randint(1000, 9999))
                user.otp = otp
                user.save()
                send_verification_code(phone_number, otp)
                return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "User not found or phone number not verified."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# OTP verification view to verify the OTP code sent to the user
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = serializer.validated_data['otp']
            user = User.objects.filter(phone_number=phone_number, otp=otp).first()
            if user:
                user.otp_verified = True
                user.otp = ''  # Clear the OTP after successful verification
                user.save()
                return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP or phone number."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Password reset view
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            new_password = serializer.validated_data['new_password']
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "User with this phone number not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
