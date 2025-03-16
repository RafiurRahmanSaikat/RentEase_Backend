from django.db.models import Prefetch, Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from interactions.models import Review
from interactions.serializers import ReviewSerializer

from .models import Category, House
from .pagination import CustomPageNumberPagination
from .serializers import CategorySerializer, HouseDetailSerializer, HouseListSerializer


class BaseViewSetWithAllPagination(viewsets.ModelViewSet):
    """Base ViewSet that handles ?page=all parameter."""

    pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Check if 'all' parameter is passed
        if request.query_params.get("page") == "all":
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "count": queryset.count(),
                    "next": None,
                    "previous": None,
                    "results": serializer.data,
                }
            )

        # Standard pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class HouseViewSet(BaseViewSetWithAllPagination):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = HouseListSerializer  # Default fallback serializer

    def get_queryset(self):
        """Optimized queryset with selective prefetching based on action"""
        qs = House.objects.select_related("owner").order_by("id")

        # Only prefetch on list and retrieve actions
        if self.action in ["list", "retrieve"]:
            # Use Prefetch for more control over the related data
            qs = qs.prefetch_related(
                "categories",
                Prefetch(
                    "reviews",
                    queryset=Review.objects.select_related("reviewer").order_by(
                        "-created_at"
                    ),
                ),
            )

        if self.request.user.is_authenticated:
            if self.request.user.role == "admin":
                return qs  # Admin can see all houses
            else:
                # Non-admin: show houses that are approved or that belong to the current user
                return qs.filter(Q(approved=True) | Q(owner=self.request.user))
        return qs.filter(approved=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, approved=False)

    def get_serializer_class(self):
        if self.action == "list":
            return HouseListSerializer
        return HouseDetailSerializer

    # Cache the list view for anonymous users for 5 minutes
    def list(self, request, *args, **kwargs):
        # Skip caching for authenticated users
        if request.user.is_authenticated:
            return super().list(request, *args, **kwargs)
        return super().list(request, *args, **kwargs)

    # Cache the detail view for anonymous users for 10 minutes
    def retrieve(self, request, *args, **kwargs):
        # Skip caching for authenticated users
        if request.user.is_authenticated:
            return super().retrieve(request, *args, **kwargs)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        house = self.get_object()
        if request.user.role == "admin" or request.user == house.owner:
            return super().update(request, *args, **kwargs)
        return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        house = self.get_object()
        if request.user != house.owner:
            return Response(
                {"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def submit_for_approval(self, request, pk=None):
        house = self.get_object()
        if request.user != house.owner:
            return Response(
                {"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN
            )
        house.approved = False
        house.save(update_fields=["approved"])
        return Response(
            {"detail": "House submitted for admin approval."}, status=status.HTTP_200_OK
        )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def approve(self, request, pk=None):
        if request.user.role != "admin":
            return Response(
                {"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN
            )
        house = self.get_object()
        house.approved = True
        house.save(update_fields=["approved"])
        return Response({"detail": "House approved."}, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def reject(self, request, pk=None):
        if request.user.role != "admin":
            return Response(
                {"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN
            )
        house = self.get_object()
        house.approved = False
        house.save(update_fields=["approved"])
        return Response({"detail": "House rejected."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def reviews(self, request, pk=None):
        house = self.get_object()
        reviews = house.reviews.select_related("reviewer").all()
        serializer = ReviewSerializer(reviews, many=True, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def add_review(self, request, pk=None):
        house = self.get_object()
        serializer = ReviewSerializer(
            data=request.data, context={"request": request, "house_id": house.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(reviewer=request.user)
        return Response(serializer.data, status=201)


class CategoryViewSet(BaseViewSetWithAllPagination):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("id")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Cache category list for 30 minutes as they change infrequently
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
