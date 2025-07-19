import asyncio
import httpx
import random
from datetime import datetime, timezone

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
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
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
        return response.status_code
    except Exception as e:
        print(f"Request failed: {e}")
        return None


async def send_batch(client, batch_size=50):
    """Send a smaller batch of requests"""
    tasks = [send_post(client, generate_payload()) for _ in range(batch_size)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for r in results if isinstance(r, int) and r == 200)
    print(f"Batch completed: {successful}/{batch_size} successful")


async def main():
    # Increased timeout and connection limits
    async with httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=100, max_connections=200),
    ) as client:

        # Test with a single request first
        print("Testing single request...")
        test_payload = generate_payload()
        try:
            response = await client.post(url, json=test_payload)
            print(f"Test request successful: {response.status_code}")
        except Exception as e:
            print(f"Test request failed: {e}")
            return

        # Send requests in smaller batches
        batch_size = 50  # Much smaller batches
        total_requests = 3000
        batches = total_requests // batch_size

        print(f"Sending {total_requests} requests in {batches} batches of {batch_size}")

        for i in range(batches):
            start = asyncio.get_event_loop().time()
            await send_batch(client, batch_size)

            # Rate limiting - wait between batches
            elapsed = asyncio.get_event_loop().time() - start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)

            print(f"Completed batch {i+1}/{batches}")


if __name__ == "__main__":
    asyncio.run(main())
