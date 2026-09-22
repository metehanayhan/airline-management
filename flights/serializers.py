from datetime import timedelta

from django.db.models import Q
from rest_framework import serializers

from .models import Flight


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            'id',
            'flight_number',
            'departure',
            'destination',
            'departure_time',
            'arrival_time',
            'airplane',
        ]
        read_only_fields = ['id']

    def validate_flight_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Flight number cannot be empty."
            )

        return value

    def validate_departure(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Departure cannot be empty."
            )

        return value

    def validate_destination(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Destination cannot be empty."
            )

        return value

    def validate(self, attrs):
        departure_time = attrs.get(
            'departure_time',
            getattr(self.instance, 'departure_time', None)
        )

        arrival_time = attrs.get(
            'arrival_time',
            getattr(self.instance, 'arrival_time', None)
        )

        airplane = attrs.get(
            'airplane',
            getattr(self.instance, 'airplane', None)
        )

        # 1. Departure < Arrival
        if departure_time and arrival_time:
            if arrival_time <= departure_time:
                raise serializers.ValidationError({
                    'arrival_time': (
                        'Arrival time must be later than departure time.'
                    )
                })

        # 2. Same airplane + minimum 1 hour gap
        if airplane and departure_time and arrival_time:

            one_hour = timedelta(hours=1)

            conflicting_flights = Flight.objects.filter(
                airplane=airplane
            ).exclude(
                pk=self.instance.pk if self.instance else None
            ).filter(
                departure_time__lt=arrival_time + one_hour,
                arrival_time__gt=departure_time - one_hour,
            )

            if conflicting_flights.exists():
                raise serializers.ValidationError({
                    'airplane': (
                        'This airplane has another flight that '
                        'conflicts with the required 1-hour gap.'
                    )
                })

        return attrs