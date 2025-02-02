from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from house.models import Advertisement
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserAccount
from .serializers import (
    RegistrationSerializer,
    UserAccountSerializer,
    UserLoginSerializer,
)


class UserInfoAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            print(
                f"Authenticated user: {user}, Token: {request.META.get('HTTP_AUTHORIZATION')}"
            )
            user_account = UserAccount.objects.get(user=user)
            user_account_serializer = UserAccountSerializer(user_account)

            return Response(user_account_serializer.data, status=status.HTTP_200_OK)
        except UserAccount.DoesNotExist:
            print("User account not found for:", user)
            return Response(
                {"error": "Invalid token or user account not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserRegisterAPIView(APIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            user = serializer.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"http://127.0.0.1:8000/account/active/{uid}/{token}/"
            email_subject = "Confirm Your Account"
            email_body = render_to_string(
                "confirm_email.html", {"confirm_link": confirm_link}
            )
            email = EmailMultiAlternatives(email_subject, "", to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()

            return Response(
                {"message": "Check Your Mail"},
                status=status.HTTP_201_CREATED,
            )
        else:
            print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailConfirmationView(APIView):
    def get(self, request, uid64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uid64).decode()
            user = User._default_manager.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user_account = UserAccount.objects.get(user=user)
                user_account.is_verified = True

                user_account.verification_token = None
                user_account.save()

                user.is_active = True
                if user_account.account_type == "Admin":
                    user.is_staff = True
                user.save()

                return Response(
                    {"message": "Email Verified successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid Token."}, status=status.HTTP_403_FORBIDDEN
                )
        except (User.DoesNotExist, UserAccount.DoesNotExist):
            return Response(
                {"error": "Invalid Verification Link."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                user_account = UserAccount.objects.get(user=user)
                if user_account.is_verified is True:
                    token, created = Token.objects.get_or_create(user=user)
                    login(request, user)
                    return Response(
                        {
                            "token": token.key,
                            "user": user.username,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Invalid Credentials"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            data={
                "errormasssage": "Something Went Wrong.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            request.user.auth_token.delete()
            logout(request)
            return Response(
                {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user_account = UserAccount.objects.get(user=request.user)
            user = request.user
            if "first_name" in request.data:
                user.first_name = request.data["first_name"]
            if "last_name" in request.data:
                user.last_name = request.data["last_name"]
            if "email" in request.data:
                user.email = request.data["email"]
            if "address" in request.data:
                user_account.address = request.data["address"]
            if "image" in request.data:
                user_account.image = request.data["image"]
            if "mobile_number" in request.data:
                user_account.mobile_number = request.data["mobile_number"]

            user.save()
            user_account.save()

            return Response(
                {"message": "Profile updated successfully"}, status=status.HTTP_200_OK
            )

        except UserAccount.DoesNotExist:

            return Response(
                {"error": "User account not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except:
            return Response(
                {"error": "Something Went Wrong "}, status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password == current_password:
            return Response(
                {"error": "New password cannot be the same as the current password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class AddFavorite(APIView):
    def post(self, request, ad_id):
        try:
            user = request.user
            advertisement = Advertisement.objects.get(id=ad_id)
            user_account = UserAccount.objects.get(user=user)
            # print(advertisement, user_account)

            if advertisement in user_account.favourites.all():
                # print(advertisement)
                return Response(
                    {"message": "Advertisement Already in Favorites."},
                    status=status.HTTP_208_ALREADY_REPORTED,
                )
            else:
                user_account.favourites.add(advertisement)
                return Response(
                    {"message": "Advertisement added to favorites."},
                    status=status.HTTP_200_OK,
                )

        except Advertisement.DoesNotExist:
            return Response(
                {"error": "Advertisement not found."}, status=status.HTTP_404_NOT_FOUND
            )


class RemoveFavorite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ad_id):
        user = request.user
        try:
            advertisement = Advertisement.objects.get(id=ad_id)
            user_account = UserAccount.objects.get(user=user)

            if advertisement in user_account.favourites.all():
                user_account.favourites.remove(advertisement)

                return Response(
                    {"message": "Advertisement removed from favorites."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Advertisement not in favorites."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Advertisement.DoesNotExist:
            return Response(
                {"error": "Advertisement not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "User account not found."}, status=status.HTTP_404_NOT_FOUND
            )
