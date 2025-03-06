from django.urls import include, path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ChangePasswordView,
    ProfileViewSet,
    RegisterView,
    ResetPasswordConfirmView,
    ResetPasswordRequestView,
    VerifyEmail,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("email-verify/", VerifyEmail.as_view(), name="email-verify"),
    path(
        "profile/",
        ProfileViewSet.as_view(
            {"get": "list", "put": "update", "patch": "partial_update"}
        ),
        name="profile",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path(
        "reset-password/",
        ResetPasswordRequestView.as_view(),
        name="reset-password-request",
    ),
    re_path(
        r"^reset-password-confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)/$",
        ResetPasswordConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
