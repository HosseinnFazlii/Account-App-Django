# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model, authenticate
from .serializers import (
    OTPSerializer, OTPVerifySerializer, UserRegistrationSerializer,
    UserUpdateSerializer, LoginSerializer
)
from accounts.utils import send_verification_code
import random

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = str(random.randint(1000, 9999))
            success, message = send_verification_code(phone_number, otp)
            if success:
                user, created = User.objects.get_or_create(phone_number=phone_number)
                user.otp = otp
                user.otp_verified = False
                user.save()
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            return Response({"error": f"Failed to send OTP: {message}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                user.otp = ""
                user.save()
                tokens = get_tokens_for_user(user)
                return Response({"message": "OTP verified successfully", **tokens}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP or phone number."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.filter(phone_number=phone_number, otp_verified=True).first()
            if user:
                user.first_name = ""
                user.last_name = ""
                user.email = ""
                user.save()
                return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            return Response({"error": "Phone number not verified."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "email": user.email,
        }
        return Response(data, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
