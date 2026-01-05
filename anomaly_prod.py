import json
import numpy as np
import pandas as pd
import joblib
from kafka import KafkaConsumer, KafkaProducer

# Load trained model
model = joblib.load("anomaly_model.pkl")

# Kafka consumer (raw orders)
consumer = KafkaConsumer(
    "orders_topic",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

# Kafka producer (anomalies only)
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

print("Anomaly ML Producer running")

DISCOUNT_THRESHOLD = 50  # % threshold

for msg in consumer:
    event = msg.value

    price = float(event["Price (Rs.)"])
    final_price = float(event["Final_Price(Rs.)"])

    discount_pct = ((price - final_price) / price) * 100 if price > 0 else 0

    # Use DataFrame to avoid sklearn warning
    features = pd.DataFrame(
        [[price, final_price]],
        columns=["Price (Rs.)", "Final_Price(Rs.)"]
    )

    ml_pred = model.predict(features)[0]

    reasons = []

    if ml_pred == -1:
        reasons.append("ML_PRICE")

    if discount_pct >= DISCOUNT_THRESHOLD:
        reasons.append("HIGH_DISCOUNT")

    print(f"Prediction={ml_pred} | ₹{price} → ₹{final_price} | reasons={reasons}")

    if reasons:
        anomaly_event = {
            "order_id": event.get("Order_ID"),
            "customer_id": event.get("User_ID"),
            "product_id": event.get("Product_ID"),
            "price": price,
            "final_price": final_price,
            "discount_pct": round(discount_pct, 2),
            "reasons": reasons,
            "raw_event": event
        }

        producer.send("anomalies.detected", anomaly_event)
        producer.flush()

        print("Anomaly sent to Kafka:", reasons)
