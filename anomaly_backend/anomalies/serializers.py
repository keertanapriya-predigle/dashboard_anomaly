from rest_framework import serializers
from .models import Anomaly

class AnomalySerializer(serializers.ModelSerializer):
    class Meta:
        model = Anomaly
        fields = [
            'id',
            'order_id',
            'customer_id',
            'product_id',
            'anomaly_type',
            'details',
            'detected_at'
        ]
