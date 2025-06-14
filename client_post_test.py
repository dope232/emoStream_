import asyncio
import httpx
import random
from datetime import datetime

url = "http://localhost:5000/api"
emojis = {
    "laugh": "😂",
    "thumbs_up": "👍",
    "thumbs_down": "👎",
    "heart": "❤️",
    "clap": "👏",
    "sad": "🙁",
}


def generate_payload():
    rkey, rvalue = random.choice(list(emojis.items()))
    x = random.randint(1, 200)
    now = datetime.now().strftime("%H:%M:%S %d:%m:%y")
    return {
        "user": f"user_{x}",
        "emoji_name": rkey,
        "emoji": rvalue,
        "timestamp": now,
    }


async def send_post(client, payload):
    try:
        response = await client.post(url, json=payload)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")


async def main():
    async with httpx.AsyncClient(timeout=5) as client:
        while True:
            start = asyncio.get_event_loop().time()
            tasks = [send_post(client, generate_payload()) for _ in range(3000)]
            await asyncio.gather(*tasks)

            # Maintain 1 second per batch
            elapsed = asyncio.get_event_loop().time() - start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)


asyncio.run(main())
