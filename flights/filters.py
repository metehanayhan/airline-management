import django_filters

from .models import Flight


class FlightFilter(django_filters.FilterSet):
    departure = django_filters.CharFilter(
        field_name='departure',
        lookup_expr='icontains'
    )

    destination = django_filters.CharFilter(
        field_name='destination',
        lookup_expr='icontains'
    )

    departure_date = django_filters.DateFilter(
        field_name='departure_time',
        lookup_expr='date'
    )

    arrival_date = django_filters.DateFilter(
        field_name='arrival_time',
        lookup_expr='date'
    )

    class Meta:
        model = Flight
        fields = [
            'departure',
            'destination',
            'departure_date',
            'arrival_date',
        ]