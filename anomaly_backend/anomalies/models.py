from django.db import models

class Anomaly(models.Model):
    order_id = models.CharField(max_length=50, null=True, blank=True)
    customer_id = models.CharField(max_length=50, null=True, blank=True)
    product_id = models.CharField(max_length=50, null=True, blank=True)

    anomaly_type = models.CharField(max_length=100)
    details = models.JSONField()

    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "anomalies"

    def __str__(self):
        return f"{self.order_id} | {self.anomaly_type}"
