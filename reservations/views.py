from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import Reservation
from .serializers import ReservationSerializer


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    queryset = (
        Reservation.objects
        .select_related('flight', 'flight__airplane')
        .all()
        .order_by('-created_at')
    )

    serializer_class = ReservationSerializer