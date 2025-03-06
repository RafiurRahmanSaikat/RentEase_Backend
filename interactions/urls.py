# interactions/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FavoriteViewSet, RentRequestViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r"rent-requests", RentRequestViewSet, basename="rent-requests")
router.register(r"reviews", ReviewViewSet, basename="reviews")
router.register(r"favorites", FavoriteViewSet, basename="favorites")

urlpatterns = [
    path("", include(router.urls)),
]
