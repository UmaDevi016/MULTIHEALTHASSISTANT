
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load env
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
if not os.path.exists(dotenv_path):
    dotenv_path = os.path.join(os.path.dirname(current_dir), ".env")

load_dotenv(dotenv_path=dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print(f"OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not Set'} (Length: {len(OPENAI_API_KEY)})")

if not OPENAI_API_KEY:
    print("ERROR: OpenAI API key not set in .env")
    exit(1)

print("\nTesting OpenAI API...")
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful translator."},
            {"role": "user", "content": "Translate 'Hello, welcome' to Hindi. Provide only the translation."},
        ],
        temperature=0.2,
        max_tokens=100
    )
    translation = response.choices[0].message.content.strip()
    print(f"✓ OpenAI Translation successful: {translation}")
except Exception as e:
    print(f"✗ OpenAI API Error: {e}")
