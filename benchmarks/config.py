import os

HOST = "localhost"
PORT = 1883
TOPIC = "benchmark"
QOS = int(os.getenv("MQTT_QOS") or 0)
AMOUNT = int(os.getenv("AMOUNT") or 1_000_000)
INTERVAL = int(os.getenv("INTERVAL") or 0)
