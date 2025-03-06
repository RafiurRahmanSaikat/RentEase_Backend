from django.utils import timezone
from rest_framework import serializers

from account.serializers import UserSerializer
from properties.models import House
from properties.serializers import HouseDetailSerializer

from .models import Favorite, RentRequest, Review


class RentRequestSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    duration = serializers.IntegerField(required=False, default=30)
    house_id = serializers.IntegerField(write_only=True)
    message = serializers.CharField(required=False)

    class Meta:
        model = RentRequest
        fields = [
            "id",
            "tenant",
            "house",
            "house_id",
            "message",
            "status",
            "paid",
            "duration",
            "created_at",
        ]
        read_only_fields = [
            "tenant",
            "house",
            "status",
            "paid",
            "created_at",
        ]

    def validate(self, data):
        house_id = data.get("house_id")
        try:
            house = House.objects.get(id=house_id)
        except House.DoesNotExist:
            raise serializers.ValidationError("House not found.")

        if house.booked_until and house.booked_until > timezone.now():
            raise serializers.ValidationError(
                f"This house is already booked until {house.booked_until}."
            )
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        house_id = validated_data.pop("house_id")
        house = House.objects.get(id=house_id)

        if house.owner == user:
            raise serializers.ValidationError(
                "You cannot send a rent request to your own house."
            )
        if RentRequest.objects.filter(house=house, tenant=user).exists():
            raise serializers.ValidationError(
                "You have already sent a rent request for this house."
            )
        rent_request = RentRequest.objects.create(
            tenant=user, house=house, **validated_data
        )
        return rent_request


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    house_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = [
            "id",
            "house_id",  # optional now; we will override it using context
            "house",
            "reviewer",
            "rating",
            "comment",
            "created_at",
        ]
        extra_kwargs = {"house": {"read_only": True}}

    def create(self, validated_data):
        # Use house_id from context if available.
        house_id = self.context.get("house_id") or validated_data.pop("house_id", None)
        if not house_id:
            raise serializers.ValidationError("house_id is required.")
        house = House.objects.get(id=house_id)
        # Do not pass reviewer here because it’s already passed in via extra kwargs in save()
        return Review.objects.create(house=house, **validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    house = HouseDetailSerializer(read_only=True)
    # (For standard POST, we won’t need body content if using URL, but we keep this for backwards compatibility)
    house_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Favorite
        fields = ["id", "house", "house_id", "created_at"]

    def create(self, validated_data):
        request = self.context["request"]
        # If house_id is provided in validated_data, use it; otherwise, error.
        if "house_id" not in validated_data:
            raise serializers.ValidationError("house_id is required.")
        house_id = validated_data.pop("house_id")
        from properties.models import House

        house = House.objects.get(id=house_id)
        # Prevent duplicate favorites.
        if Favorite.objects.filter(user=request.user, house=house).exists():
            raise serializers.ValidationError("Favorite already exists.")
        return Favorite.objects.create(user=request.user, house=house)
