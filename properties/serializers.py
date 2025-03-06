from django.contrib.auth import get_user_model
from rest_framework import serializers

from interactions.models import Review

from .models import Category, House

User = get_user_model()


# Serializer for categories remains unchanged.
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


# -------------------------------
# House List Serializer (Lightweight)
# -------------------------------
class HouseListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = House
        fields = [
            "id",
            "title",
            "description",
            "location",
            "price",
            "images",
            "approved",
            "categories",
            "owner_name",
            "review_count",
            "average_rating",
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        total = sum(review.rating for review in reviews)
        return round(total / reviews.count(), 2)


# -------------------------------
# Owner Detail Serializer for House Detail
# -------------------------------
class OwnerDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="username")
    owner_first_name = serializers.CharField(source="first_name")
    owner_last_name = serializers.CharField(source="last_name")

    class Meta:
        model = User
        fields = [
            "owner_username",
            "owner_first_name",
            "owner_last_name",
            "email",
            "phone",
            "image",
        ]


# -------------------------------
# Review Detail Serializer for House Detail
# -------------------------------
class ReviewDetailSerializer(serializers.ModelSerializer):
    reviewer_full_name = serializers.CharField(
        source="reviewer.username", read_only=True
    )
    reviewer_avatar = serializers.CharField(source="reviewer.image", read_only=True)
    reviewer_email = serializers.EmailField(source="reviewer.email", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "reviewer_full_name",
            "reviewer_avatar",
            "reviewer_email",
            "rating",
            "comment",
            "created_at",
        ]


# -------------------------------
# House Detail Serializer (Full details)
# -------------------------------
class HouseDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    owner = OwnerDetailSerializer(read_only=True)
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = ReviewDetailSerializer(many=True, read_only=True)
    # reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # For writes, we use a list of category IDs.
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Category.objects.all(), source="categories"
    )

    class Meta:
        model = House
        fields = [
            "id",
            "title",
            "description",
            "location",
            "price",
            "images",
            "approved",
            "categories",
            "category_ids",
            "owner",
            "review_count",
            "average_rating",
            "created_at",
            "reviews",
        ]

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        total = sum(review.rating for review in reviews)
        return round(total / reviews.count(), 2)

    def update(self, instance, validated_data):
        # Pop categories if present
        categories = validated_data.pop("categories", None)
        update_fields = []
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            update_fields.append(attr)
        instance.save(update_fields=update_fields)
        if categories is not None:
            instance.categories.set(categories)
        return instance


# class HouseDetailSerializer(serializers.ModelSerializer):
#     categories = CategorySerializer(many=True, read_only=True)
#     owner_username = serializers.CharField(source="owner.username", read_only=True)
#     owner_first_name = serializers.CharField(source="owner.first_name", read_only=True)
#     owner_last_name = serializers.CharField(source="owner.last_name", read_only=True)
#     owner_avatar = serializers.CharField(source="owner.image", read_only=True)
#     review_count = serializers.SerializerMethodField()
#     average_rating = serializers.SerializerMethodField()
#     reviews = ReviewDetailSerializer(many=True, read_only=True)
#     # reviews = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#     # For writes, we use a list of category IDs.
#     category_ids = serializers.PrimaryKeyRelatedField(
#         many=True, write_only=True, queryset=Category.objects.all(), source="categories"
#     )

#     class Meta:
#         model = House
#         fields = [
#             "id",
#             "title",
#             "description",
#             "location",
#             "price",
#             "images",
#             "approved",
#             "categories",
#             "category_ids",
#             "owner_username",
#             "owner_first_name",
#             "owner_last_name",
#             "owner_avatar",
#             "review_count",
#             "average_rating",
#             "created_at",
#             "reviews",
#         ]

#     def get_review_count(self, obj):
#         return obj.reviews.count()

#     def get_average_rating(self, obj):
#         reviews = obj.reviews.all()
#         if not reviews:
#             return None
#         total = sum(review.rating for review in reviews)
#         return round(total / reviews.count(), 2)

#     def update(self, instance, validated_data):
#         # Pop categories if present
#         categories = validated_data.pop("categories", None)
#         update_fields = []
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#             update_fields.append(attr)
#         instance.save(update_fields=update_fields)
#         if categories is not None:
#             instance.categories.set(categories)
#         return instance
