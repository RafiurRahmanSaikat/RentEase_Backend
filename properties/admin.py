from django.contrib import admin

from .models import Category, House


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "location", "price", "approved", "created_at")
    list_filter = ("approved", "owner", "categories")
    search_fields = ("title", "description", "location")
    ordering = ("-created_at",)
