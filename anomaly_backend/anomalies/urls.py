from django.urls import path
from .views import anomaly_stream

# urlpatterns = [
#     path('anomalies/', get_anomalies, name='get-anomalies'),

# ]

# urls.py
urlpatterns = [
    path("stream/anomalies/", anomaly_stream),
]

