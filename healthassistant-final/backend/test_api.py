"""
Enhanced test script with better output capture
This will help identify exactly what's happening with translation
"""
import requests
import json
import sys

def test_translation():
    url = "http://localhost:8000/translate"
    
    test_cases = [
        {"text": "Hello", "target_lang": "hi", "expected": "Hindi"},
        {"text": "Good morning", "target_lang": "ta", "expected": "Tamil"},
        {"text": "How are you?", "target_lang": "te", "expected": "Telugu"},
    ]
    
    print("="*70)
    print("TRANSLATION API TEST")
    print("="*70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Translating to {test['expected']}")
        print(f"Input: {test['text']}")
        print(f"Target: {test['target_lang']}")
        print("-"*70)
        
        try:
            response = requests.post(url, json=test, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                translation = data.get('translated_text', '')
                
                print(f"✓ Status: {response.status_code}")
                print(f"✓ Translation: {translation}")
                
                # Check if it's demo mode
                if "[Demo Mode" in translation or "डेमो" in translation:
                    print("⚠️  WARNING: Using DEMO MODE (APIs failed)")
                elif translation == test['text']:
                    print("⚠️  WARNING: No translation occurred")
                else:
                    print("✓ SUCCESS: Real translation received")
                    
            else:
                print(f"✗ Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("✗ ERROR: Cannot connect to backend")
            print("Make sure backend is running: py backend/app.py")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Exception: {e}")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nIf you see 'DEMO MODE' warnings:")
    print("  1. Check your .env file has valid API keys")
    print("  2. Check backend console for detailed error messages")
    print("  3. Verify API keys are correct on respective platforms")
    print("\nBackend should show detailed logs like:")
    print("  [Lingo] Calling API: ...")
    print("  [Lingo] Status Code: ...")
    print("  [OpenAI] Calling API: ...")
    print("="*70)

if __name__ == "__main__":
    test_translation()
