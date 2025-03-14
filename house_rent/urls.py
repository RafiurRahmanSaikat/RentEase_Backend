# house_rent/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from account.views import UserViewSet

router = DefaultRouter()


router.register(r"users", UserViewSet, basename="admin-users")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("account.urls")),
    path("api/properties/", include("properties.urls")),
    path("api/interactions/", include("interactions.urls")),
    # path("silk/", include("silk.urls", namespace="silk")),
    # Register the router URLs
    path("api/admin/", include(router.urls)),
    # YOUR PATTERNS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
