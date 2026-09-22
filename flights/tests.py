from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airplanes.models import Airplane
from flights.models import Flight


class FlightAPITestCase(APITestCase):

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
            tail_number='TC-FLIGHT01',
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

        self.flight_data = {
            'flight_number': 'TK-TEST01',
            'departure': 'Istanbul',
            'destination': 'Ankara',
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
            'airplane': self.airplane.id,
        }

    def test_create_flight(self):
        response = self.client.post(
            '/flights/',
            self.flight_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['flight_number'],
            'TK-TEST01'
        )

    def test_list_flights(self):
        Flight.objects.create(
            flight_number='TK-TEST01',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        response = self.client.get(
            '/flights/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_get_flight_detail(self):
        flight = Flight.objects.create(
            flight_number='TK-TEST01',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        response = self.client.get(
            f'/flights/{flight.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['flight_number'],
            'TK-TEST01'
        )

    def test_update_flight(self):
        flight = Flight.objects.create(
            flight_number='TK-TEST01',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        response = self.client.patch(
            f'/flights/{flight.id}/',
            {
                'destination': 'Izmir'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['destination'],
            'Izmir'
        )

    def test_delete_flight(self):
        flight = Flight.objects.create(
            flight_number='TK-TEST01',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        response = self.client.delete(
            f'/flights/{flight.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Flight.objects.filter(
                id=flight.id
            ).exists()
        )

    def test_create_flight_with_invalid_time(self):
        data = self.flight_data.copy()

        data['arrival_time'] = (
            self.departure_time - timedelta(hours=1)
        ).isoformat()

        response = self.client.post(
            '/flights/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'arrival_time',
            response.data
        )

    def test_create_flight_with_conflict(self):
        Flight.objects.create(
            flight_number='TK-EXISTING',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        conflicting_data = self.flight_data.copy()

        conflicting_data['flight_number'] = 'TK-CONFLICT'

        conflicting_data['departure_time'] = (
            self.departure_time + timedelta(hours=1)
        ).isoformat()

        conflicting_data['arrival_time'] = (
            self.departure_time + timedelta(hours=3)
        ).isoformat()

        response = self.client.post(
            '/flights/',
            conflicting_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'airplane',
            response.data
        )

    def test_filter_by_departure(self):
        Flight.objects.create(
            flight_number='TK-IST',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        response = self.client.get(
            '/flights/?departure=istanbul'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['departure'],
            'Istanbul'
        )

    def test_filter_by_destination(self):
        Flight.objects.create(
            flight_number='TK-ANK',
            departure='Istanbul',
            destination='Ankara',
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
            airplane=self.airplane,
        )

        response = self.client.get(
            '/flights/?destination=ankara'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['destination'],
            'Ankara'
        )