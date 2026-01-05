""" from kafka import KafkaConsumer
import json
import numpy as np
import joblib

consumer = KafkaConsumer(
    'orders_topic',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

model = joblib.load("anomaly_model.pkl")
print("Anomaly detection started (Price + Final_Price)...")

for msg in consumer:
    event = msg.value
    price = float(event.get('Price (Rs.)', 0))
    final_price = float(event.get('Final_Price(Rs.)', 0))
    
    features = np.array([[price, final_price]])
    anomaly = model.predict(features)[0]
    
    if anomaly == -1:
        # SAVE TO DJANGO DB!
        Anomaly.objects.create(
            user_id=event.get('User_ID'),
            product_id=event.get('Product_ID'),
            category=event.get('Category'),
            price=price,
            final_price=final_price,
            discount_pct=float(event.get('Discount (%)', 0)),
            details=f"Price:₹{price}→₹{final_price}"
        )
        print(f"🚨 SAVED ANOMALY to DB!") """

# # kafka_cons.py
"""""
import os
import sys
import json
import numpy as np
import joblib
from kafka import KafkaConsumer

# 🔥 ADD DJANGO PROJECT ROOT TO PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DJANGO_PROJECT_PATH = os.path.join(BASE_DIR, "anomaly_backend")

sys.path.append(DJANGO_PROJECT_PATH)

# 🔥 SET DJANGO SETTINGS MODULE
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "anomaly_backend.settings"
)

import django
django.setup()

# 🔥 NOW SAFE TO IMPORT MODELS
from anomalies.models import Anomaly
from django.utils import timezone

consumer = KafkaConsumer(
    'orders_topic',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

model = joblib.load("anomaly_model.pkl")
print("🚀 Anomaly detection started (Price + Final_Price)...")
from anomalies.models import Anomaly
from django.utils import timezone

Anomaly.objects.create(
    order_id="TEST",
    customer_id="TEST",
    product_id="TEST",
    anomaly_type="TEST_INSERT",
    details={"test": True},
    detected_at=timezone.now()
)

print("✅ TEST anomaly inserted")


for msg in consumer:
    event = msg.value

    price = float(event.get('Price (Rs.)', 0))
    final_price = float(event.get('Final_Price(Rs.)', 0))

    features = np.array([[price, final_price]])
    prediction = model.predict(features)[0]

    if prediction == -1:
        discount_pct = ((price - final_price) / price * 100) if price > 0 else 0

        print(f"🚨 FRAUD ALERT | ₹{price} → ₹{final_price} ({discount_pct:.1f}%)")

        # 🔥 SAVE TO POSTGRES VIA DJANGO
        Anomaly.objects.create(
            order_id=str(event.get("Order_ID")),
            customer_id=str(event.get("User_ID")),
            product_id=str(event.get("Product_ID")),
            anomaly_type="ML Price Anomaly",
            details=event,
            detected_at=timezone.now()
        )
 """
import os
import sys
import json
import numpy as np
import pandas as pd
import joblib
from kafka import KafkaConsumer

# ============================
# DJANGO SETUP
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DJANGO_PROJECT_PATH = os.path.join(BASE_DIR, "anomaly_backend")

sys.path.append(DJANGO_PROJECT_PATH)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "anomaly_backend.settings"
)

import django
django.setup()

from anomalies.models import Anomaly
from django.utils import timezone

# ============================
# LOAD ML MODEL
# ============================
MODEL_PATH = os.path.join(BASE_DIR, "anomaly_model.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("❌ anomaly_model.pkl not found")

model = joblib.load(MODEL_PATH)
print("✅ ML model loaded")

# ============================
# KAFKA CONSUMER
# ============================
consumer = KafkaConsumer(
    "orders_topic",
    bootstrap_servers="localhost:9092",
    group_id="anomaly-consumer-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("🚀 Anomaly detection consumer started...")

# ============================
# CONSUME MESSAGES
# ============================
for msg in consumer:
    try:
        event = msg.value

        # ------------------------
        # Extract values safely
        # ------------------------
        price = float(event.get("Price (Rs.)", 0))
        final_price = float(event.get("Final_Price(Rs.)", 0))

        if price <= 0:
            continue

        discount_pct = ((price - final_price) / price) * 100

        # ------------------------
        # ML prediction (no warning)
        # ------------------------
        features = pd.DataFrame(
            [[price, final_price]],
            columns=["Price (Rs.)", "Final_Price(Rs.)"]
        )

        prediction = model.predict(features)[0]

        print(
            f"Prediction={prediction} | "
            f"₹{price} → ₹{final_price} | "
            f"Discount={discount_pct:.1f}%"
        )

        # ------------------------
        # HYBRID LOGIC (IMPORTANT)
        # ------------------------
        is_anomaly = prediction == -1 or discount_pct >= 40

        if not is_anomaly:
            continue

        print("🚨 ANOMALY DETECTED → saving to DB")

        # ------------------------
        # SAVE TO POSTGRES
        # ------------------------
        Anomaly.objects.create(
            order_id=str(event.get("Order_ID", "NA")),
            customer_id=str(event.get("User_ID", "NA")),
            product_id=str(event.get("Product_ID", "NA")),
            anomaly_type="ML + RULE Price Anomaly",
            details=event,
            detected_at=timezone.now()
        )

        print("✅ Saved anomaly")

    except Exception as e:
        print("❌ Error processing message:", e)
