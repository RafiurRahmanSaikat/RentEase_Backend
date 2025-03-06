# properties/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, HouseViewSet

router = DefaultRouter()
router.register(r"houses", HouseViewSet, basename="houses")
router.register(r"categories", CategoryViewSet, basename="categories")

urlpatterns = [
    path("", include(router.urls)),
]
