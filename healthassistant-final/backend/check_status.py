"""
Status check script - writes to file to avoid encoding issues
"""
import requests
import json

def check_status():
    url = "http://localhost:8000/translate"
    test = {"text": "Hello", "target_lang": "hi"}
    
    print("Running status check...")
    
    with open('status_result.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("TRANSLATION API STATUS CHECK\n")
        f.write("="*70 + "\n")
        
        f.write(f"\nTesting: {test['text']} -> Hindi\n")
        f.write("-" * 70 + "\n")

        try:
            response = requests.post(url, json=test, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                translation = data.get('translated_text', '')
                
                f.write(f"Status: {response.status_code} OK\n")
                f.write(f"Translation received: YES\n")
                f.write(f"Length: {len(translation)} characters\n")
                
                # Check mode
                if "[Demo Mode" in translation:
                    f.write("\nMODE: DEMO MODE (Both APIs failed)\n")
                    f.write(f"DEBUG ERROR: {data.get('debug_error', 'Unknown')}\n")
                    f.write(f"LINGO STATUS: {data.get('lingo_status', 'Unknown')}\n")
                    f.write("ACTION: Check backend console for error details\n")
                elif "डेमो" in translation or "demo" in translation.lower():
                    f.write("\nMODE: DEMO MODE (Both APIs failed)\n")
                    f.write(f"DEBUG ERROR: {data.get('debug_error', 'Unknown')}\n")
                    f.write(f"LINGO STATUS: {data.get('lingo_status', 'Unknown')}\n")
                    f.write("ACTION: Check backend console for error details\n")
                else:
                    f.write("\nMODE: REAL TRANSLATION (API working!)\n")
                    f.write("SUCCESS: Translation is working correctly\n")
                    
                # Show first 50 chars
                preview = translation[:50] + "..." if len(translation) > 50 else translation
                f.write(f"\nPreview: {repr(preview)}\n")
                    
            else:
                f.write(f"ERROR: Status {response.status_code}\n")
                f.write(f"Response: {response.text}\n")
                
        except requests.exceptions.ConnectionError:
            f.write("ERROR: Cannot connect to backend\n")
            f.write("Make sure backend is running: py app.py\n")
        except Exception as e:
            f.write(f"ERROR: {e}\n")

    print("Status check complete. Results written to status_result.txt")

if __name__ == "__main__":
    check_status()
