from django.urls import path
from anomalies.consumers import AnomalyConsumer

websocket_urlpatterns = [
    path("ws/anomalies/", AnomalyConsumer.as_asgi()),
]
