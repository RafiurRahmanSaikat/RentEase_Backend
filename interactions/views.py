import stripe
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Favorite, RentRequest, Review
from .serializers import FavoriteSerializer, RentRequestSerializer, ReviewSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

import stripe
from django.conf import settings
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import RentRequest
from .serializers import RentRequestSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class RentRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RentRequestSerializer
    queryset = RentRequest.objects.select_related("house", "tenant").all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin" or user.is_superuser:
            return RentRequest.objects.select_related("house", "tenant").all()
        return RentRequest.objects.select_related("house", "tenant").filter(
            Q(tenant=user) | Q(house__owner=user)
        )

    def get_object(self):
        try:
            return super().get_object()
        except Exception:
            raise NotFound(
                "Rent request not found for the current user. Check that you are logged in as either the tenant or the house owner and that the ID is correct."
            )

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def accept(self, request, pk=None):
        rent_request = self.get_object()
        # Allow if current user is either the owner or admin.
        if (
            request.user != rent_request.house.owner
            and request.user.role != "admin"
            and not request.user.is_superuser
        ):
            return Response({"detail": "Not allowed."}, status=403)
        rent_request.status = "accepted"
        rent_request.save()
        return Response({"detail": "Rent request accepted."})

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def reject(self, request, pk=None):
        rent_request = self.get_object()
        if (
            request.user != rent_request.house.owner
            and request.user.role != "admin"
            and not request.user.is_superuser
        ):
            return Response(
                {"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN
            )
        rent_request.status = "rejected"
        rent_request.save()
        return Response({"detail": "Rent request rejected."}, status=status.HTTP_200_OK)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def pay(self, request, pk=None):
        rent_req = self.get_object()
        if rent_req.tenant != request.user or rent_req.status != "approved":
            return Response(
                {"detail": "Not allowed to pay."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(rent_req.house.price * 100),  # price in cents
                currency="usd",
                payment_method_types=["card"],
                description=f"Payment for house: {rent_req.house.title}",
            )
            # Payment successful; mark rent request as paid.
            rent_req.paid = True
            rent_req.save(update_fields=["paid"])

            # Book the house: calculate the booking end date.
            duration_days = rent_req.duration  # duration provided in the rent request
            rent_req.house.booked_until = timezone.now() + datetime.timedelta(
                days=duration_days
            )
            rent_req.house.save(update_fields=["booked_until"])

            return Response(
                {
                    "detail": f"Payment successful. House booked until {rent_req.house.booked_until}.",
                    "client_secret": intent.client_secret,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related("house", "reviewer").all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.select_related("house", "user").all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    # Standard POST using JSON body is still supported.
    # Additionally, add custom actions to add/remove via URL.
    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def add(self, request, pk=None):
        # Here, pk is interpreted as the house id.
        from properties.models import House

        try:
            house = House.objects.get(id=pk)
        except House.DoesNotExist:
            return Response(
                {"detail": "House not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if Favorite.objects.filter(user=request.user, house=house).exists():
            return Response(
                {"detail": "Favorite already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite = Favorite.objects.create(user=request.user, house=house)
        serializer = self.get_serializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def remove(self, request, pk=None):
        from properties.models import House

        try:
            house = House.objects.get(id=pk)
        except House.DoesNotExist:
            return Response(
                {"detail": "House not found."}, status=status.HTTP_404_NOT_FOUND
            )
        favorite = self.get_queryset().filter(house=house)
        if favorite.exists():
            favorite.delete()
            return Response(
                {"detail": "Removed from favorites."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Favorite not found."}, status=status.HTTP_404_NOT_FOUND
            )
