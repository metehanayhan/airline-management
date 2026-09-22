from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import FlightFilter
from .models import Flight
from .serializers import FlightSerializer
from reservations.serializers import ReservationSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects
        .select_related('airplane')
        .all()
        .order_by('departure_time')
    )

    serializer_class = FlightSerializer

    filterset_class = FlightFilter

    @action(
        detail=True,
        methods=['get'],
        url_path='reservations'
    )
    def reservations(self, request, pk=None):
        flight = self.get_object()

        reservations = (
            flight.reservations
            .all()
            .order_by('-created_at')
        )

        serializer = ReservationSerializer(
            reservations,
            many=True
        )

        return Response(serializer.data)