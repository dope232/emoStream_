import streamlit as st
from confluent_kafka import Consumer
import json 
import time 
import streamlit.components.v1 as components

st.title("Emo Stream- Real Time Streaming of Emoji Bursts")
bubble_js = """
<style>
  #chat-area { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
  .bubble {
    position: absolute;
    background: #2196F3; color: white;
    padding: 8px 12px;
    border-radius: 16px;
    opacity: 0;
    animation: floatin 4s ease-out forwards;
  }
  @keyframes floatin {
    0% { transform: translateY(0px); opacity: 1; }
    80% { opacity: 0.8; }
    100% { transform: translateY(-120px) scale(1.2); opacity: 0; }
  }
</style>
<div id="chat-area"></div>
<script>
  const area = document.getElementById('chat-area');
  window.addBubble = msg => {
    const b = document.createElement('div');
    b.className = 'bubble';
    b.innerText = msg;
    b.style.left = Math.random() * 80 + 'vw';
    area.appendChild(b);
    setTimeout(() => b.remove(), 4000);
  };
</script>
"""
components.html(bubble_js, height=0, width=0)


consumer_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "emoji-visualizer-group",
    "auto.offset.reset": "earliest",

}

KAFKA_TOPIC = "topic2"

consumer = Consumer(consumer_conf)

consumer.subscribe([KAFKA_TOPIC])


def main():
    try:
        while True:
            msg = consumer.poll(5.0)
            if msg is None:
                continue
            if msg.error():
                print(f"consumer error: {msg.error()}")
                continue
            else:
                value = msg.value().decode('utf-8')
                result_dict = json.loads(value)
                with st.container():
                    components.html(value,  height=0)




    

    except Exception as e:
        print(f"Error at {e}")

























if st.button("Start the emoji stream"):

