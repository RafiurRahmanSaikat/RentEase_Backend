from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class House(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="houses", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.TextField(help_text="Comma separated image URLs")
    categories = models.ManyToManyField("Category", related_name="houses")
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    booked_until = models.DateTimeField(blank=True, null=True)  # New field

    def __str__(self):
        return self.title
