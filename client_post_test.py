import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import json


url = "http://localhost:5000/api"
emojis = {
    "smile": "😊",
    "laugh": "😂",
    "thumbs_up": "👍",
    "thumbs_down": "👎",
    "heart": "❤️",
    "fire": "🔥",
    "clap": "👏",
    "star": "⭐",
    "thinking": "🤔",
    "sunglasses": "😎",
}

rkey, rvalue = random.choice(list(emojis.items()))
x = random.randint(1, 200)
now = datetime.now()
formatted_timestamp = now.strftime("%H:%M:%S %d:%m:%y")

post_payload = {
    "user": f"user_{x}",
    "emoji_name": rkey,
    "emoji": rvalue,
    "timestamp": formatted_timestamp,
}

while True:
    rkey, rvalue = random.choice(list(emojis.items()))
    x = random.randint(1, 200)
    now = datetime.now()
    formatted_timestamp = now.strftime("%H:%M:%S %d:%m:%y")

    post_payload = {
        "user": f"user_{x}",
        "emoji_name": rkey,
        "emoji": rvalue,
        "timestamp": formatted_timestamp,
    }
    response = requests.post(url, json=post_payload)
    time.sleep(2)
    print(response.text)
