from django.db import models


class RouteReport(models.Model):
    departure = models.CharField(
        max_length=100
    )
    destination = models.CharField(
        max_length=100
    )
    total_flights = models.PositiveIntegerField()
    total_seats = models.PositiveIntegerField()
    used_seats = models.PositiveIntegerField()
    occupancy_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    most_used_plane_model = models.CharField(
        max_length=100
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['departure', 'destination'],
                name='unique_route_report'
            )
        ]

    def __str__(self):
        return f"{self.departure} → {self.destination}"