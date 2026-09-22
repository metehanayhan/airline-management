from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from airplanes.models import Airplane
from flights.models import Flight
from reports.models import RouteReport
from reservations.models import Reservation


class RouteReportCommandTestCase(TestCase):

    def setUp(self):
        self.airplane = Airplane.objects.create(
            tail_number='TC-REPORT01',
            model='Airbus A320',
            capacity=180,
            production_year=2020,
            status=True,
        )

        departure_time = (
            timezone.now() + timedelta(days=1)
        )

        arrival_time = (
            departure_time + timedelta(hours=2)
        )

        self.flight = Flight.objects.create(
            flight_number='TK-REPORT01',
            departure='Istanbul',
            destination='Ankara',
            departure_time=departure_time,
            arrival_time=arrival_time,
            airplane=self.airplane,
        )

    def test_generate_route_report(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'route_report.xlsx'

            call_command(
                'generate_route_report',
                output=str(output_path)
            )

        report = RouteReport.objects.get(
            departure='Istanbul',
            destination='Ankara'
        )

        self.assertEqual(
            report.total_flights,
            1
        )

        self.assertEqual(
            report.total_seats,
            180
        )

        self.assertEqual(
            report.used_seats,
            0
        )

        self.assertEqual(
            report.occupancy_rate,
            Decimal('0.00')
        )

        self.assertEqual(
            report.most_used_plane_model,
            'Airbus A320'
        )

    def test_report_counts_active_reservations(self):
        Reservation.objects.create(
            passenger_name='Metehan Ayhan',
            passenger_email='metehan@example.com',
            reservation_code='REPORT1',
            flight=self.flight,
            status=True,
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'route_report.xlsx'

            call_command(
                'generate_route_report',
                output=str(output_path)
            )

        report = RouteReport.objects.get(
            departure='Istanbul',
            destination='Ankara'
        )

        self.assertEqual(
            report.used_seats,
            1
        )

        self.assertEqual(
            report.occupancy_rate,
            Decimal('0.56')
        )

    def test_report_ignores_cancelled_reservations(self):
        Reservation.objects.create(
            passenger_name='Cancelled Passenger',
            passenger_email='cancelled@example.com',
            reservation_code='REPORT2',
            flight=self.flight,
            status=False,
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'route_report.xlsx'

            call_command(
                'generate_route_report',
                output=str(output_path)
            )

        report = RouteReport.objects.get(
            departure='Istanbul',
            destination='Ankara'
        )

        self.assertEqual(
            report.used_seats,
            0
        )

        self.assertEqual(
            report.occupancy_rate,
            Decimal('0.00')
        )

    def test_report_is_updated_instead_of_duplicated(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'route_report.xlsx'

            call_command(
                'generate_route_report',
                output=str(output_path)
            )

        first_count = RouteReport.objects.filter(
            departure='Istanbul',
            destination='Ankara'
        ).count()

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / 'route_report.xlsx'

            call_command(
                'generate_route_report',
                output=str(output_path)
            )

        second_count = RouteReport.objects.filter(
            departure='Istanbul',
            destination='Ankara'
        ).count()

        self.assertEqual(
            first_count,
            1
        )

        self.assertEqual(
            second_count,
            1
        )