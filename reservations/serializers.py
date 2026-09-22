import secrets
import string

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from rest_framework import serializers

from flights.models import Flight

from .models import Reservation


def generate_reservation_code(length=8):
    characters = string.ascii_uppercase + string.digits

    while True:
        code = ''.join(
            secrets.choice(characters)
            for _ in range(length)
        )

        if not Reservation.objects.filter(
            reservation_code=code
        ).exists():
            return code


def send_confirmation_email(reservation):
    flight = reservation.flight

    send_mail(
        subject=f'Reservation Confirmation - {reservation.reservation_code}',
        message=(
            f'Your reservation has been confirmed.\n\n'
            f'Reservation Code: {reservation.reservation_code}\n'
            f'Flight Number: {flight.flight_number}\n'
            f'Route: {flight.departure} -> {flight.destination}\n'
            f'Departure: {flight.departure_time}\n'
            f'Arrival: {flight.arrival_time}\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reservation.passenger_email],
        fail_silently=True,
    )


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id',
            'passenger_name',
            'passenger_email',
            'reservation_code',
            'flight',
            'status',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'reservation_code',
            'created_at',
        ]

    def validate_passenger_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Passenger name cannot be empty."
            )

        return value

    def validate_passenger_email(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Passenger email cannot be empty."
            )

        return value

    def validate(self, attrs):
        flight = attrs.get(
            'flight',
            getattr(self.instance, 'flight', None)
        )

        new_status = attrs.get(
            'status',
            getattr(self.instance, 'status', True)
        )

        # Yeni aktif reservation oluşturuluyorsa
        creating_active = (
            self.instance is None and new_status
        )

        # Mevcut cancelled reservation tekrar aktif yapılıyorsa
        reactivating = (
            self.instance is not None
            and not self.instance.status
            and new_status
        )

        if flight and (creating_active or reactivating):

            active_reservations = Reservation.objects.filter(
                flight=flight,
                status=True
            ).exclude(
                pk=self.instance.pk if self.instance else None
            ).count()

            if active_reservations >= flight.airplane.capacity:
                raise serializers.ValidationError({
                    'flight': 'This flight is fully booked.'
                })

        return attrs

    def create(self, validated_data):
        with transaction.atomic():

            flight = (
                Flight.objects
                .select_for_update()
                .select_related('airplane')
                .get(pk=validated_data['flight'].pk)
            )

            status = validated_data.get('status', True)

            if status:
                active_reservations = Reservation.objects.filter(
                    flight=flight,
                    status=True
                ).count()

                if active_reservations >= flight.airplane.capacity:
                    raise serializers.ValidationError({
                        'flight': 'This flight is fully booked.'
                    })

            validated_data['flight'] = flight
            validated_data['reservation_code'] = (
                generate_reservation_code()
            )

            reservation = Reservation.objects.create(
                **validated_data
            )

            transaction.on_commit(
                lambda: send_confirmation_email(reservation)
            )

            return reservation