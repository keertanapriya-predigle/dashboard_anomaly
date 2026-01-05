from django.urls import path
from .views import anomaly_stream

urlpatterns = [
    path("stream/anomalies/", anomaly_stream),
]

