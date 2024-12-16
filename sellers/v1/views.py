from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from sellers.models import SellerStore, Category, State, City
from sellers.v1.serializers import (
    SellerStoreSerializer,
    CategorySerializer,
    StateSerializer,
    CitySerializer,
)

class SellerStoreRegisterView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allow handling of files

    def post(self, request):
        """Register a new store for the logged-in user."""
        try:
            # Check if the user already has a registered store
            if SellerStore.objects.filter(user=request.user).exists():
                return Response(
                    {"error": "You already have a registered store."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Handle JSON data and file uploads
            data = request.data.copy()
            data['phone'] = getattr(request.user, 'phone_number', None)  # Use 'phone_number' field
            serializer = SellerStoreSerializer(data=data)

            if serializer.is_valid():
                # Save the store with the user linked
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellerStoreUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allow handling of files

    def put(self, request):
        """Fully update store information."""
        try:
            # Retrieve the store for the logged-in user
            store = SellerStore.objects.get(user=request.user)
            serializer = SellerStoreSerializer(store, data=request.data, partial=False)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except SellerStore.DoesNotExist:
            return Response(
                {"error": "You do not have a registered store."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellerStorePartialUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allow handling of files

    def patch(self, request):
        """Partially update store information."""
        try:
            # Retrieve the store for the logged-in user
            store = SellerStore.objects.get(user=request.user)
            serializer = SellerStoreSerializer(store, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except SellerStore.DoesNotExist:
            return Response(
                {"error": "You do not have a registered store."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryListView(APIView):
    def get(self, request):
        """Retrieve the list of categories."""
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StateCityListView(APIView):
    def get(self, request):
        """Retrieve the list of states and cities."""
        try:
            states = State.objects.all()
            state_serializer = StateSerializer(states, many=True)

            cities = City.objects.all()
            city_serializer = CitySerializer(cities, many=True)

            return Response(
                {"states": state_serializer.data, "cities": city_serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
