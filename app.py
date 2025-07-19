import streamlit as st
from confluent_kafka import Consumer
import json 
import time 
import streamlit.components.v1 as components

st.title("Emo Stream- Real Time Streaming of Emoji Bursts")

# Initialize the bubble display area
if 'bubble_container' not in st.session_state:
    st.session_state.bubble_container = st.empty()

# Simple display placeholder
placeholder = st.empty()


consumer_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": f"emoji-visualizer-group-{int(time.time())}",
    "auto.offset.reset": "latest",
    "enable.auto.commit": True,
    "session.timeout.ms": 6000,
    "default.topic.config": {"auto.offset.reset": "latest"}
}

KAFKA_TOPIC = "topic2"

consumer = Consumer(consumer_conf)

consumer.subscribe([KAFKA_TOPIC])


def main():
    try:
        print("Starting to poll for messages...")
        while True:
            msg = consumer.poll(5.0)
            if msg is None:
                print("No message received, continuing...")
                continue
            if msg.error():
                print(f"consumer error: {msg.error()}")
                continue
            else:
                value = msg.value().decode('utf-8')
                print(f"Received message: {value}")
                
                result_dict = json.loads(value)
                emoji_data = json.loads(value)
                emoji_text = f"{emoji_data['emoji']} {emoji_data['emoji_name']}"
                
                print(f"Displaying: {emoji_text}")
                
                # Simple display that should work
                placeholder.markdown(f"### {emoji_text}")
                time.sleep(0.5)  # Brief pause to see the emoji
    except Exception as e:
        print(f"Error at {e}")

if st.button("Start the emoji stream"):
    main()