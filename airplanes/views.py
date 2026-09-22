from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Airplane
from .serializers import AirplaneSerializer
from flights.serializers import FlightSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().order_by('id')
    serializer_class = AirplaneSerializer

    @action(
        detail=True,
        methods=['get'],
        url_path='flights'
    )
    def flights(self, request, pk=None):
        airplane = self.get_object()

        flights = airplane.flights.all().order_by('departure_time')

        serializer = FlightSerializer(
            flights,
            many=True
        )

        return Response(serializer.data)