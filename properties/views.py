from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Import ReviewSerializer from interactions
from interactions.serializers import ReviewSerializer

from .models import Category, House
from .serializers import CategorySerializer, HouseDetailSerializer, HouseListSerializer


class HouseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = HouseListSerializer  # Default fallback serializer

    def get_queryset(self):
        qs = House.objects.select_related("owner")
        # Only prefetch on list and retrieve actions
        if self.action in ["list", "retrieve"]:
            qs = qs.prefetch_related("categories", "reviews")
        if self.request.user.is_authenticated:
            if self.request.user.role == "admin":
                return qs  # Admin can see all houses.
            else:
                # Non-admin: show houses that are approved or that belong to the current user.
                return qs.filter(Q(approved=True) | Q(owner=self.request.user))
        return qs.filter(approved=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, approved=False)

    def get_serializer_class(self):
        if self.action == "list":
            return HouseListSerializer
        return HouseDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, approved=False)

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
        reviews = house.reviews.all()
        from interactions.serializers import ReviewSerializer  # lazy import

        serializer = ReviewSerializer(reviews, many=True, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def add_review(self, request, pk=None):
        house = self.get_object()
        from interactions.serializers import ReviewSerializer  # lazy import

        serializer = ReviewSerializer(
            data=request.data, context={"request": request, "house_id": house.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(reviewer=request.user)
        return Response(serializer.data, status=201)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
