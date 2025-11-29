"""
Debug script to test translation APIs directly
Run this to diagnose translation issues
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LINGO_API_KEY = os.getenv("LINGO_API_KEY", "")
LINGO_PROJECT_ID = os.getenv("LINGO_PROJECT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print("=" * 60)
print("TRANSLATION API DEBUG SCRIPT")
print("=" * 60)

# Check environment variables
print("\n1. ENVIRONMENT VARIABLES CHECK:")
print(f"   LINGO_API_KEY: {'✓ SET' if LINGO_API_KEY else '✗ NOT SET'}")
print(f"   LINGO_PROJECT_ID: {'✓ SET' if LINGO_PROJECT_ID else '✗ NOT SET'}")
print(f"   OPENAI_API_KEY: {'✓ SET' if OPENAI_API_KEY else '✗ NOT SET'}")

if LINGO_API_KEY:
    print(f"   LINGO_API_KEY (first 10 chars): {LINGO_API_KEY[:10]}...")
if LINGO_PROJECT_ID:
    print(f"   LINGO_PROJECT_ID: {LINGO_PROJECT_ID}")

# Test Lingo.dev API
async def test_lingo_api():
    print("\n2. TESTING LINGO.DEV API:")
    if not LINGO_API_KEY or not LINGO_PROJECT_ID:
        print("   ✗ Skipping - API key or Project ID not set")
        return False
    
    test_text = "Hello, how are you?"
    target_lang = "hi"
    
    # Try different possible endpoint formats
    endpoints = [
        f"https://api.lingo.dev/v1/projects/{LINGO_PROJECT_ID}/translate",
        f"https://api.lingo.dev/v1/translate",
        f"https://lingo.dev/api/v1/projects/{LINGO_PROJECT_ID}/translate",
    ]
    
    for endpoint in endpoints:
        print(f"\n   Testing endpoint: {endpoint}")
        try:
            payload = {"text": test_text, "target": target_lang, "source": "auto"}
            headers = {
                "Authorization": f"Bearer {LINGO_API_KEY}",
                "Content-Type": "application/json"
            }
            
            print(f"   Request payload: {payload}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                
                print(f"   Status Code: {response.status_code}")
                print(f"   Response Headers: {dict(response.headers)}")
                print(f"   Response Body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✓ SUCCESS!")
                    print(f"   Response data: {data}")
                    
                    # Try to extract translation
                    translation = data.get("translation") or data.get("translatedText") or data.get("result")
                    if translation:
                        print(f"   ✓ Translation found: {translation}")
                        return True
                    else:
                        print(f"   ✗ Translation not found in response")
                else:
                    print(f"   ✗ Failed with status {response.status_code}")
                    
        except Exception as e:
            print(f"   ✗ Exception: {type(e).__name__}: {str(e)}")
    
    return False

# Test OpenAI API
def test_openai_api():
    print("\n3. TESTING OPENAI API:")
    if not OPENAI_API_KEY:
        print("   ✗ Skipping - API key not set")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        test_text = "Hello, how are you?"
        target_lang = "Hindi"
        
        prompt = f"Translate the following text to {target_lang}: {test_text}"
        
        print(f"   Testing with prompt: {prompt}")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=100
        )
        
        translation = response.choices[0].message.content.strip()
        print(f"   ✓ SUCCESS!")
        print(f"   Translation: {translation}")
        return True
        
    except Exception as e:
        print(f"   ✗ Exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Run tests
async def main():
    lingo_success = await test_lingo_api()
    openai_success = test_openai_api()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"   Lingo.dev API: {'✓ WORKING' if lingo_success else '✗ FAILED'}")
    print(f"   OpenAI API: {'✓ WORKING' if openai_success else '✗ FAILED'}")
    
    if not lingo_success and not openai_success:
        print("\n⚠️  BOTH APIs FAILED - Translation will use demo mode")
    elif not lingo_success:
        print("\n⚠️  Lingo.dev failed - Translation will use OpenAI fallback")
    elif not openai_success:
        print("\n✓ Lingo.dev working - Translation should work")
    else:
        print("\n✓ Both APIs working - Translation should work perfectly")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
