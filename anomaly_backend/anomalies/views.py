# views.py
# from django.http import StreamingHttpResponse
# import json, time
# from .models import Anomaly
# from django.utils.timezone import localtime

# def anomaly_stream(request):
#     def event_stream():
#         while True:
#             anomalies = list(
#                 Anomaly.objects
#                 .order_by('-detected_at')[:20]
#                 .values(
#                     "customer_id",
#                     "product_id",
#                     "anomaly_type",
#                     "details",
#                     "detected_at",
#                 )
#             )
#             for a in anomalies:
#                 a['detected_at'] = localtime(a['detected_at']).isoformat()

#             yield f"data: {json.dumps(anomalies)}\n\n"
#             time.sleep(5)
#     return StreamingHttpResponse(
#         event_stream(),
#         content_type='text/event-stream'
#     )

import json, time
from django.http import StreamingHttpResponse
from django.utils.timezone import now
from .models import Anomaly


def anomaly_stream(request):
    def event_stream():
        last_seen = None

        while True:
            qs = Anomaly.objects.order_by("detected_at")

            if last_seen:
                qs = qs.filter(detected_at__gt=last_seen)

            anomalies = list(
                qs.values(
                    "id",
                    "customer_id",
                    "product_id",
                    "anomaly_type",
                    "details",
                    "detected_at",
                )
            )

            if anomalies:
                last_seen = anomalies[-1]["detected_at"]

                for a in anomalies:
                    a["detected_at"] = a["detected_at"].isoformat()

                yield f"data: {json.dumps(anomalies)}\n\n"

            time.sleep(2)

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
