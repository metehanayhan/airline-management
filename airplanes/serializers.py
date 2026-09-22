from datetime import datetime

from rest_framework import serializers

from .models import Airplane


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = [
            'id',
            'tail_number',
            'model',
            'capacity',
            'production_year',
            'status',
        ]
        read_only_fields = ['id']

    def validate_tail_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Tail number cannot be empty."
            )

        return value

    def validate_model(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Aircraft model cannot be empty."
            )

        return value

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Capacity must be greater than 0."
            )

        return value

    def validate_production_year(self, value):
        current_year = datetime.now().year

        if value < 1900 or value > current_year:
            raise serializers.ValidationError(
                f"Production year must be between 1900 and {current_year}."
            )

        return value