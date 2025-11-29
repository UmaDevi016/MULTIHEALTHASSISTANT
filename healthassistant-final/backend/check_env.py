
import os
from dotenv import load_dotenv
import httpx
import asyncio

# Logic from app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
if not os.path.exists(dotenv_path):
    # Fallback to root directory
    dotenv_path = os.path.join(os.path.dirname(current_dir), ".env")

print(f"Checking for .env at: {dotenv_path}")
if os.path.exists(dotenv_path):
    print("Found .env file")
else:
    print("ERROR: .env file NOT found")

load_dotenv(dotenv_path=dotenv_path)

LINGO_API_KEY = os.getenv("LINGO_API_KEY", "")
LINGO_PROJECT_ID = os.getenv("LINGO_PROJECT_ID", "")

print(f"LINGO_API_KEY: {'Set' if LINGO_API_KEY else 'Not Set'} (Length: {len(LINGO_API_KEY)})")
print(f"LINGO_PROJECT_ID: {'Set' if LINGO_PROJECT_ID else 'Not Set'} (Length: {len(LINGO_PROJECT_ID)})")

async def test_lingo():
    if not LINGO_API_KEY or not LINGO_PROJECT_ID:
        print("Skipping Lingo test due to missing keys")
        return

    print("\nTesting Lingo API...")
    url = f"https://api.lingo.dev/v1/projects/{LINGO_PROJECT_ID}/translate"
    payload = {"text": "Hello", "target": "es", "source": "auto"}
    headers = {"Authorization": f"Bearer {LINGO_API_KEY}"}
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=headers)
            print(f"Status Code: {r.status_code}")
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

async def test_connectivity():
    print("\nTesting connectivity to google.com...")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://google.com")
            print(f"Google Status: {r.status_code}")
    except Exception as e:
        print(f"Google Connectivity Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connectivity())
    asyncio.run(test_lingo())
