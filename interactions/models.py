from django.conf import settings
from django.db import models

from properties.models import House


class RentRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rent_requests"
    )
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="rent_requests"
    )
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    paid = models.BooleanField(default=False)
    duration = models.PositiveIntegerField(help_text="Duration in days", default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RentRequest by {self.tenant} for {self.house}"


class Review(models.Model):
    house = models.ForeignKey(House, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="reviews", on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} on {self.house.title}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="favorites", on_delete=models.CASCADE
    )
    house = models.ForeignKey(
        House, related_name="favorited_by", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "house")

    def __str__(self):
        return f"{self.user.username} - {self.house.title}"
