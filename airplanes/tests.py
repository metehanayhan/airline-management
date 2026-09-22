from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from airplanes.models import Airplane


class AirplaneAPITestCase(APITestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.airplane_data = {
            'tail_number': 'TC-TEST01',
            'model': 'Airbus A320',
            'capacity': 180,
            'production_year': 2020,
            'status': True,
        }

    def test_create_airplane(self):
        response = self.client.post(
            '/airplanes/',
            self.airplane_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['tail_number'],
            'TC-TEST01'
        )

        self.assertEqual(
            response.data['capacity'],
            180
        )

    def test_list_airplanes(self):
        Airplane.objects.create(
            **self.airplane_data
        )

        response = self.client.get(
            '/airplanes/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    def test_get_airplane_detail(self):
        airplane = Airplane.objects.create(
            **self.airplane_data
        )

        response = self.client.get(
            f'/airplanes/{airplane.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['tail_number'],
            'TC-TEST01'
        )

    def test_update_airplane(self):
        airplane = Airplane.objects.create(
            **self.airplane_data
        )

        response = self.client.patch(
            f'/airplanes/{airplane.id}/',
            {
                'model': 'Boeing 737',
                'capacity': 190,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['model'],
            'Boeing 737'
        )

        self.assertEqual(
            response.data['capacity'],
            190
        )

    def test_delete_airplane(self):
        airplane = Airplane.objects.create(
            **self.airplane_data
        )

        response = self.client.delete(
            f'/airplanes/{airplane.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Airplane.objects.filter(
                id=airplane.id
            ).exists()
        )

    def test_create_airplane_with_invalid_capacity(self):
        data = self.airplane_data.copy()
        data['capacity'] = 0

        response = self.client.post(
            '/airplanes/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'capacity',
            response.data
        )

    def test_create_airplane_with_invalid_production_year(self):
        data = self.airplane_data.copy()
        data['production_year'] = 1800

        response = self.client.post(
            '/airplanes/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'production_year',
            response.data
        )

    def test_create_airplane_with_empty_tail_number(self):
        data = self.airplane_data.copy()
        data['tail_number'] = '   '

        response = self.client.post(
            '/airplanes/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'tail_number',
            response.data
        )

    def test_create_airplane_with_duplicate_tail_number(self):
        Airplane.objects.create(
            **self.airplane_data
        )

        response = self.client.post(
            '/airplanes/',
            self.airplane_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'tail_number',
            response.data
        )
