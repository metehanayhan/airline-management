from django.db import models


class Airplane(models.Model):
    tail_number = models.CharField(
        max_length=20,
        unique=True
    )
    model = models.CharField(
        max_length=100
    )
    capacity = models.PositiveIntegerField()
    production_year = models.PositiveIntegerField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tail_number} - {self.model}"