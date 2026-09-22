from django.db import models

from flights.models import Flight


class Reservation(models.Model):
    passenger_name = models.CharField(
        max_length=150
    )
    passenger_email = models.EmailField()
    reservation_code = models.CharField(
        max_length=20,
        unique=True
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name='reservations'
    )
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reservation_code} - {self.passenger_name}"