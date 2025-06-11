from flask import Flask, request, jsonify
from confluent_kafka import Producer
import uuid
import json

app = Flask(__name__)


producer_conf = {"bootstrap.servers": "localhost:9092", "linger.ms": 500}

producer = Producer(producer_conf)


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(
            f"✅ Delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )


@app.route("/api", methods=["POST"])
def produce():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON payload"}), 400

    try:
        value = json.dumps(data)
        key = str(uuid.uuid4())

        producer.produce(topic="topic1", key=key, value=value, callback=delivery_report)
        producer.poll(0)
        return jsonify({"status": "Message enqueued", "uuid_key": key}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
