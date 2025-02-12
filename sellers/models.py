from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class SellerStore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, unique=True)  # This should auto-fill from User model
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="seller/logos/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    instagram_id = models.CharField(max_length=255, blank=True, null=True)  # Added Instagram ID
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically fill the phone field with the seller's phone number."""
        if not self.phone:
            self.phone = self.user.phone_number  # Auto-fill phone from the User model
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.phone_number})"
