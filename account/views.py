# account/views.py
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import ProfileUpdateSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        self.send_verification_email(user)

    def send_verification_email(self, user):
        # Generate JWT token for email verification
        token = jwt.encode({"user_id": user.id}, settings.SECRET_KEY, algorithm="HS256")

        # Create verification link
        current_site = get_current_site(self.request).domain
        relativeLink = reverse("email-verify")
        absurl = f"http://{current_site}{relativeLink}?token={token}"

        # Render HTML email template
        email_body = render_to_string(
            "emails/verification_email.html",
            {"username": user.username, "verification_link": absurl},
        )

        # Send email
        send_mail(
            subject="Verify your email - RentEase",
            message="",  # Plain text fallback
            html_message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class VerifyEmail(views.APIView):
    def get(self, request):
        token = request.GET.get("token")
        try:
            # Decode JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Find and activate user
            user = User.objects.get(id=payload["user_id"])
            if not user.is_email_verified:
                user.is_email_verified = True
                user.is_active = True
                user.save()

            return Response(
                {"email": "Successfully activated"}, status=status.HTTP_200_OK
            )

        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activation link expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        new_password2 = request.data.get("new_password2")

        # Validate current password
        if not user.check_password(current_password):
            return Response(
                {"detail": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate new passwords match
        if new_password != new_password2:
            return Response(
                {"detail": "New passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set and save new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class ResetPasswordRequestView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Find user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate password reset token
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create reset link
        current_site = get_current_site(request).domain
        reset_link = f"http://{current_site}{reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})}"

        # Render HTML email template
        email_body = render_to_string(
            "emails/password_reset_request.html",
            {"username": user.username, "reset_link": reset_link},
        )

        # Send password reset email
        send_mail(
            subject="Password Reset Request - RentEase",
            message="",  # Plain text fallback
            html_message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Password reset link sent."}, status=status.HTTP_200_OK
        )


class ResetPasswordConfirmView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        new_password = request.data.get("new_password")
        new_password2 = request.data.get("new_password2")

        # Validate new passwords match
        if new_password != new_password2:
            return Response(
                {"detail": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Decode user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate reset token
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set and save new password
        user.set_password(new_password)
        user.save()

        # Send confirmation email
        email_body = render_to_string(
            "emails/password_reset_confirmation.html",
            {
                "username": user.username,
            },
        )

        send_mail(
            subject="Password Reset Successful - RentEase",
            message="",  # Plain text fallback
            html_message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Password reset successful."}, status=status.HTTP_200_OK
        )


class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def get_queryset(self):
        # Only return the current user
        return User.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        # Always return the current user
        return self.request.user

    def list(self, request, *args, **kwargs):
        # Return current user's profile
        serializer = UserSerializer(self.get_object())
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # Full update of user profile
        partial = False
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        # Partial update of user profile
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


# class ProfileViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # Only return the current user
#         return User.objects.filter(pk=self.request.user.pk)

#     def get_object(self):
#         # Always return the current user
#         return self.request.user

#     def list(self, request, *args, **kwargs):
#         # Override list to return the current user's profile
#         serializer = self.get_serializer(self.get_object())
#         return Response(serializer.data)

#     def get_serializer_class(self):
#         if self.request.method == "GET":
#             return UserSerializer
#         return ProfileUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]


# import jwt
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.contrib.sites.shortcuts import get_current_site
# from django.core.mail import send_mail
# from django.urls import reverse
# from django.utils.encoding import force_bytes, force_str
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from rest_framework import generics, permissions, status, views, viewsets
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response

# from .serializers import ProfileUpdateSerializer, RegisterSerializer, UserSerializer

# User = get_user_model()


# class RegisterView(generics.CreateAPIView):
#     serializer_class = RegisterSerializer
#     permission_classes = [AllowAny]

#     def perform_create(self, serializer):
#         user = serializer.save()
#         self.send_verification_email(user)

#     def send_verification_email(self, user):
#         token = jwt.encode({"user_id": user.id}, settings.SECRET_KEY, algorithm="HS256")
#         current_site = get_current_site(self.request).domain
#         relativeLink = reverse("email-verify")
#         absurl = f"http://{current_site}{relativeLink}?token={token}"
#         email_body = (
#             f"Hi {user.username},\nUse the link below to verify your email:\n{absurl}"
#         )
#         send_mail(
#             subject="Verify your email",
#             message=email_body,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[user.email],
#             fail_silently=False,
#         )


# class VerifyEmail(views.APIView):
#     def get(self, request):
#         token = request.GET.get("token")
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#             user = User.objects.get(id=payload["user_id"])
#             if not user.is_email_verified:
#                 user.is_email_verified = True
#                 user.is_active = True
#                 user.save()
#             return Response(
#                 {"email": "Successfully activated"}, status=status.HTTP_200_OK
#             )
#         except jwt.ExpiredSignatureError:
#             return Response(
#                 {"error": "Activation link expired"}, status=status.HTTP_400_BAD_REQUEST
#             )
#         except jwt.exceptions.DecodeError:
#             return Response(
#                 {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
#             )


# class ProfileViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # Only return the current user.
#         return User.objects.filter(pk=self.request.user.pk)

#     def get_object(self):
#         # Always return the current user.
#         return self.request.user

#     def list(self, request, *args, **kwargs):
#         # Override list to return the current user's profile.
#         serializer = self.get_serializer(self.get_object())
#         return Response(serializer.data)

#     def get_serializer_class(self):
#         if self.request.method == "GET":
#             return UserSerializer
#         return ProfileUpdateSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#     permission_classes = [AllowAny]


# # -------------------------------
# # Password Change & Reset Views
# # -------------------------------


# class ChangePasswordView(views.APIView):

#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         current_password = request.data.get("current_password")
#         new_password = request.data.get("new_password")
#         new_password2 = request.data.get("new_password2")
#         if not user.check_password(current_password):
#             return Response(
#                 {"detail": "Current password is incorrect."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         if new_password != new_password2:
#             return Response(
#                 {"detail": "New passwords do not match."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         user.set_password(new_password)
#         user.save()
#         return Response(
#             {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
#         )


# class ResetPasswordRequestView(views.APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get("email")
#         if not email:
#             return Response(
#                 {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response(
#                 {"detail": "User with this email does not exist."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         token_generator = PasswordResetTokenGenerator()
#         token = token_generator.make_token(user)
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         current_site = get_current_site(request).domain
#         reset_link = f"http://{current_site}{reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})}"
#         email_body = f"Hi {user.username},\nUse the link below to reset your password:\n{reset_link}"
#         send_mail(
#             subject="Reset your password",
#             message=email_body,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[user.email],
#             fail_silently=False,
#         )
#         return Response(
#             {"detail": "Password reset link sent."}, status=status.HTTP_200_OK
#         )


# class ResetPasswordConfirmView(views.APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, uidb64, token):
#         new_password = request.data.get("new_password")
#         new_password2 = request.data.get("new_password2")
#         if new_password != new_password2:
#             return Response(
#                 {"detail": "Passwords do not match."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             return Response(
#                 {"detail": "Invalid uid."}, status=status.HTTP_400_BAD_REQUEST
#             )
#         token_generator = PasswordResetTokenGenerator()
#         if not token_generator.check_token(user, token):
#             return Response(
#                 {"detail": "Invalid or expired token."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         user.set_password(new_password)
#         user.save()
#         return Response(
#             {"detail": "Password reset successful."}, status=status.HTTP_200_OK
#         )
