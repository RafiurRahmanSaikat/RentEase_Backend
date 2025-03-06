# account/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("admin", "Admin"),
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    is_email_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username
