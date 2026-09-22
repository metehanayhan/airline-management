from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airplanes.models import Airplane
from flights.models import Flight
from reservations.models import Reservation


class ReservationAPITestCase(APITestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.airplane = Airplane.objects.create(
            tail_number='TC-RES01',
            model='Airbus A320',
            capacity=180,
            production_year=2020,
            status=True,
        )

        self.departure_time = (
            timezone.now() + timedelta(days=1)
        )

        self.arrival_time = (
            self.departure_time + timedelta(hours=2)
        )

        self.flight = Flight.objects.create(
            flight_number='TK-RES01',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        self.reservation_data = {
            'passenger_name': 'Metehan Ayhan',
            'passenger_email': 'metehan@example.com',
            'flight': self.flight.id,
            'status': True,
        }

    def test_create_reservation(self):
        response = self.client.post(
            '/reservations/',
            self.reservation_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['passenger_name'],
            'Metehan Ayhan'
        )

        self.assertTrue(
            response.data['status']
        )

        self.assertIn(
            'reservation_code',
            response.data
        )

        self.assertGreaterEqual(
            len(response.data['reservation_code']),
            5
        )

    def test_list_reservations(self):
        Reservation.objects.create(
            passenger_name='Metehan Ayhan',
            passenger_email='metehan@example.com',
            reservation_code='TEST01',
            flight=self.flight,
            status=True,
        )

        response = self.client.get(
            '/reservations/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_get_reservation_detail(self):
        reservation = Reservation.objects.create(
            passenger_name='Metehan Ayhan',
            passenger_email='metehan@example.com',
            reservation_code='TEST01',
            flight=self.flight,
            status=True,
        )

        response = self.client.get(
            f'/reservations/{reservation.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['reservation_code'],
            'TEST01'
        )

    def test_update_reservation(self):
        reservation = Reservation.objects.create(
            passenger_name='Metehan Ayhan',
            passenger_email='metehan@example.com',
            reservation_code='TEST01',
            flight=self.flight,
            status=True,
        )

        response = self.client.patch(
            f'/reservations/{reservation.id}/',
            {
                'passenger_name': 'Updated Passenger'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['passenger_name'],
            'Updated Passenger'
        )

    def test_reservation_code_is_generated_automatically(self):
        response = self.client.post(
            '/reservations/',
            self.reservation_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        reservation_code = response.data[
            'reservation_code'
        ]

        self.assertIsNotNone(
            reservation_code
        )

        self.assertGreaterEqual(
            len(reservation_code),
            5
        )

        self.assertTrue(
            reservation_code.isalnum()
        )

    def test_reservation_code_cannot_be_changed(self):
        reservation = Reservation.objects.create(
            passenger_name='Metehan Ayhan',
            passenger_email='metehan@example.com',
            reservation_code='TEST01',
            flight=self.flight,
            status=True,
        )

        response = self.client.patch(
            f'/reservations/{reservation.id}/',
            {
                'reservation_code': 'CHANGED01'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['reservation_code'],
            'TEST01'
        )

        reservation.refresh_from_db()

        self.assertEqual(
            reservation.reservation_code,
            'TEST01'
        )

    def test_create_reservation_when_flight_is_full(self):
        self.airplane.capacity = 1
        self.airplane.save()

        Reservation.objects.create(
            passenger_name='First Passenger',
            passenger_email='first@example.com',
            reservation_code='FIRST1',
            flight=self.flight,
            status=True,
        )

        response = self.client.post(
            '/reservations/',
            self.reservation_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'flight',
            response.data
        )

    def test_cancelled_reservation_does_not_count_as_occupied(self):
        self.airplane.capacity = 1
        self.airplane.save()

        Reservation.objects.create(
            passenger_name='Cancelled Passenger',
            passenger_email='cancelled@example.com',
            reservation_code='CANCEL1',
            flight=self.flight,
            status=False,
        )

        response = self.client.post(
            '/reservations/',
            self.reservation_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_cancel_reservation(self):
        reservation = Reservation.objects.create(
            passenger_name='Metehan Ayhan',
            passenger_email='metehan@example.com',
            reservation_code='TEST01',
            flight=self.flight,
            status=True,
        )

        response = self.client.patch(
            f'/reservations/{reservation.id}/',
            {
                'status': False
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertFalse(
            response.data['status']
        )

        reservation.refresh_from_db()

        self.assertFalse(
            reservation.status
        )

    def test_create_reservation_with_invalid_email(self):
        data = self.reservation_data.copy()

        data['passenger_email'] = 'invalid-email'

        response = self.client.post(
            '/reservations/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'passenger_email',
            response.data
        )