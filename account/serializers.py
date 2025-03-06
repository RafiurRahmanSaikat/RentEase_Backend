from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "address",
            "image",
            "role",
            "is_email_verified",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
            "phone",
            "address",
            "image",
            "role",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        # If role is not explicitly admin, force it to 'user'
        # if validated_data.get("role") != "admin":
        #     validated_data["role"] = "user"
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # User must verify email first
        user.save()
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "image",
            "role",
        ]
        # This is more concise than listing every field
        extra_kwargs = {field: {"required": False} for field in fields}

    def validate(self, data):
        # More efficient to check both fields in one method
        # This reduces database queries by checking both in one go
        user = self.context["request"].user

        # Only validate email if it's being updated
        if "email" in data and data["email"] != user.email:
            if User.objects.filter(email=data["email"]).exclude(pk=user.pk).exists():
                raise serializers.ValidationError(
                    {"email": "This email is already in use."}
                )

        # Only validate username if it's being updated
        if "username" in data and data["username"] != user.username:
            if (
                User.objects.filter(username=data["username"])
                .exclude(pk=user.pk)
                .exists()
            ):
                raise serializers.ValidationError(
                    {"username": "This username is already in use."}
                )

        return data

    def update(self, instance, validated_data):
        # This performs a single update operation regardless of how many fields are changed
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
