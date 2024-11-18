from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from .serializers import (
    OTPSerializer, OTPVerifySerializer, UserUpdateSerializer, LoginSerializer
)
from accounts.utils import send_verification_code
import random
from django.utils import timezone
from datetime import timedelta
from wallet.models import Wallet


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
            otp = str(random.randint(1000, 9999))  # Generate a random 4-digit OTP
            
            # Send OTP code using SMS API
            success, message = send_verification_code(phone_number, otp)
            if success:
                user, created = User.objects.get_or_create(phone_number=phone_number)
                user.otp = otp
                user.otp_created_at = timezone.now()  # Set the OTP creation time
                user.otp_verified = False  # Mark as unverified until OTP is validated
                user.save()
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            else:
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
                # Check if the OTP is expired
                expiration_time = timedelta(minutes=2)
                if timezone.now() - user.otp_created_at > expiration_time:
                    return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

                # If OTP is valid and not expired, verify the user
                user.otp_verified = True
                user.otp = ''  # Clear the OTP
                user.save()

                # Automatically create a wallet for the user if not already created
                wallet, created = Wallet.objects.get_or_create(user=user)

                # Generate JWT tokens and return them
                tokens = get_tokens_for_user(user)
                return Response({
                    "message": "OTP verified successfully.",
                    "wallet": {
                        "id": wallet.id,
                        "balance": wallet.balance,
                        "currency": wallet.currency,
                    },
                    "tokens": tokens
                }, status=status.HTTP_200_OK)

            return Response({"error": "Invalid OTP or phone number."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(phone_number=phone_number)
                # Using check_password to verify raw password with hashed password
                if user.check_password(password):
                    tokens = get_tokens_for_user(user)
                    return Response(tokens, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        print("Updating user:", request.user)
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("User updated successfully in the database.")
            return Response({"message": "User updated successfully."}, status=status.HTTP_200_OK)
        print("Errors during update:", serializer.errors)
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
