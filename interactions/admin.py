from django.contrib import admin

from .models import Favorite, RentRequest, Review


@admin.register(RentRequest)
class RentRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "house", "status", "paid", "created_at")
    list_filter = ("status", "paid", "created_at")
    search_fields = ("house__title", "requester__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("house", "reviewer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("house__title", "reviewer__username", "comment")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "house", "created_at")
    search_fields = ("user__username", "house__title")
