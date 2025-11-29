# backend/app.py
"""FastAPI backend for Multilingual Health Assistant - humanized & minimal."""

import os
import sqlite3
import threading
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import openai
from dotenv import load_dotenv
from web3 import Web3


# optional TTS
try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

current_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(current_dir, ".env")
if not os.path.exists(dotenv_path):
    # Fallback to root directory
    dotenv_path = os.path.join(os.path.dirname(current_dir), ".env")
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

LINGO_API_KEY = os.getenv("LINGO_API_KEY", "")
LINGO_PROJECT_ID = os.getenv("LINGO_PROJECT_ID", "")
LINGO_PROJECT_ID = os.getenv("LINGO_PROJECT_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://cloudflare-eth.com") # Public RPC

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))


print(f"LINGO_API_KEY: {'Set' if LINGO_API_KEY else 'Not Set'}")
print(f"LINGO_PROJECT_ID: {'Set' if LINGO_PROJECT_ID else 'Not Set'}")
print(f"OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not Set'}")

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "reminders.db"))

app = FastAPI(title="Multilingual Health Assistant API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo/hackathon only. Lock down in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB init
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine TEXT NOT NULL,
            dosage TEXT,
            time TEXT,
            language TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

# Models
class TranslateRequest(BaseModel):
    text: str
    target_lang: str

class SpeakRequest(BaseModel):
    text: str
    target_lang: str = "en"

class ReminderRequest(BaseModel):
    medicine: str
    dosage: str
    time: str
    language: str = "en"

class EthBalanceRequest(BaseModel):
    address: str

class EthPaymentRequest(BaseModel):
    sender: str
    amount: float
    service: str


# Helpers
def google_translate(text: str, target: str) -> str:
    """Use Google Translate via deep-translator (Python 3.13 compatible)"""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target=target)
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"[Google Translate] Error: {e}")
        raise RuntimeError(f"Google Translate failed: {str(e)}")

async def call_lingo_translate(text: str, target: str) -> str | None:
    if not LINGO_API_KEY or not LINGO_PROJECT_ID:
        return "ERROR: API key or Project ID not configured"
    try:
        url = f"https://api.lingo.dev/v1/projects/{LINGO_PROJECT_ID}/translate"
        payload = {"text": text, "target": target, "source": "auto"}
        headers = {"Authorization": f"Bearer {LINGO_API_KEY}"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(url, json=payload, headers=headers)
            
            if r.status_code == 200:
                data = r.json()
                translation = data.get("translation") or data.get("translatedText") or data.get("result")
                if translation:
                    return translation
                else:
                    return f"ERROR: No translation found in response: {data}"
            else:
                return f"ERROR: API returned status {r.status_code}: {r.text}"
    except Exception as e:
        return f"ERROR: Exception: {str(e)}"

def openai_translate(text: str, target: str) -> str:
    if not OPENAI_API_KEY:
        print("[OpenAI] API key not configured")
        raise RuntimeError("OpenAI key not configured.")
    
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    language_names = {
        "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali",
        "ml": "Malayalam", "mr": "Marathi", "or": "Odia",
        "es": "Spanish", "fr": "French", "ar": "Arabic", "en": "English"
    }
    target_name = language_names.get(target, target)
    prompt = (
        f"You are a translator writing for elderly users. Translate the text below into {target_name}. "
        "Use short, clear sentences and easy words.\n\n"
        f"Text: {text}\n\nTranslation:"
    )
    
    print(f"[OpenAI] Calling API with model gpt-3.5-turbo")
    print(f"[OpenAI] Target language: {target_name}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=400
        )
        translation = response.choices[0].message.content.strip()
        print(f"[OpenAI] ✓ Translation successful: {translation}")
        return translation
    except Exception as e:
        print(f"[OpenAI] ✗ Exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"OpenAI translation failed: {str(e)}")

def speak_text_in_background(text: str):
    if not TTS_AVAILABLE:
        return
    def _worker(t):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 120)
            engine.setProperty("volume", 0.9)
            engine.say(t)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_worker, args=(text,), daemon=True).start()

# Endpoints
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}

@app.post("/translate")
async def translate(req: TranslateRequest):
    text = req.text.strip()
    target = req.target_lang.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required.")
    
    print(f"\n{'='*60}")
    print(f"[Translation Request] Text: '{text}' → Target: '{target}'")
    print(f"{'='*60}")
    
    
    # Try Google Translate first (free and reliable)
    print("\n[Step 1] Trying Google Translate...")
    try:
        translation = google_translate(text, target)
        print(f"\n[Success] Translation completed via Google Translate")
        print(f"\n[Final Result] {translation}")
        print(f"{'='*60}\n")
        return {"translated_text": translation, "target_lang": target, "success": True}
    except Exception as google_error:
        print(f"\n[Step 2] Google Translate failed ({google_error}), trying OpenAI API...")
        
        # Try OpenAI as fallback
        try:
            translation = openai_translate(text, target)
            print(f"\n[Success] Translation completed via OpenAI")
            print(f"\n[Final Result] {translation}")
            print(f"{'='*60}\n")
            return {"translated_text": translation, "target_lang": target, "success": True}
        except Exception as exc:
            # If both fail, provide a demo translation
            print(f"\n[Step 3] Both APIs failed, using demo mode")
            print(f"[Error] {exc}")
            
            # Simple demo translations for testing
            demo_translations = {
                "hi": "यह एक डेमो अनुवाद है: " + text,
                "ta": "இது ஒரு டெமோ மொழிபெயர்ப்பு: " + text,
                "te": "ఇది డెమో అనువాదం: " + text,
                "bn": "এটি একটি ডেমো অনুবাদ: " + text,
                "ml": "ഇത് ഒരു ഡെമോ വിവർത്തനം: " + text,
                "mr": "हे डेमो भाषांतर आहे: " + text,
                "or": "ଏହା ଏକ ଡେମୋ ଅନୁବାଦ: " + text,
                "es": "Esta es una traducción de demostración: " + text,
                "fr": "Ceci est une traduction de démonstration: " + text,
                "ar": "هذه ترجمة تجريبية: " + text,
                "en": text
            }
            
            if target in demo_translations:
                translation = demo_translations[target]
            else:
                translation = f"[Demo Mode - API Error] {text}"
            
            print(f"[Demo] Using demo translation: {translation}")
            print(f"[Config] Google Translate: Failed")
            print(f"[Config] OpenAI API Key: {'SET' if OPENAI_API_KEY else 'NOT SET'}")
            
            # Return error details for debugging
            return {
                "translated_text": translation, 
                "target_lang": target, 
                "success": False,
                "debug_error": str(exc),
                "google_status": str(google_error),
                "openai_status": "Failed"
            }


@app.post("/speak")
def speak(req: SpeakRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required for speech.")
    speak_text_in_background(text)
    return {"status": "Speech started (background)", "language": req.target_lang}

@app.post("/add-reminder")
def add_reminder(req: ReminderRequest):
    if not req.medicine.strip():
        raise HTTPException(status_code=400, detail="Medicine name required.")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reminders (medicine, dosage, time, language) VALUES (?, ?, ?, ?)",
        (req.medicine.strip(), req.dosage.strip(), req.time.strip(), req.language.strip())
    )
    conn.commit()
    rem_id = cur.lastrowid
    conn.close()
    return {"status": "Reminder added", "reminder_id": rem_id}

@app.get("/reminders")
def get_reminders():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, medicine, dosage, time, language, created_at FROM reminders ORDER BY time ASC")
    rows = cur.fetchall()
    conn.close()
    reminders = [
        {"id": r[0], "medicine": r[1], "dosage": r[2], "time": r[3], "language": r[4], "created_at": r[5]}
        for r in rows
    ]
    return {"reminders": reminders, "count": len(reminders)}

@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    if deleted:
        return {"status": "deleted", "id": reminder_id}
    raise HTTPException(status_code=404, detail="Reminder not found.")

@app.post("/emergency-alert")
def emergency_alert(payload: Dict[str, Any]):
    msg = payload.get("message", "Health emergency")
    caregiver = payload.get("caregiver_contact", "")
    # In production, integrate Twilio / SMS / Email. Here we simulate.
    return {
        "status": "Emergency alert activated (simulated)",
        "message": msg,
        "caregiver_contact": caregiver,
        "sent_at": datetime.utcnow().isoformat() + "Z",
        "notifications_sent": ["sms(simulated)", "email(simulated)"]
    }

@app.post("/eth/balance")
def get_eth_balance(req: EthBalanceRequest):
    try:
        if not w3.is_address(req.address):
            raise HTTPException(status_code=400, detail="Invalid Ethereum address")
        
        # Get balance in Wei and convert to Ether
        balance_wei = w3.eth.get_balance(req.address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        return {
            "address": req.address,
            "balance_eth": float(balance_eth),
            "balance_wei": balance_wei,
            "connected": w3.is_connected()
        }
    except Exception as e:
        print(f"ETH Error: {e}")
        # Return mock data if RPC fails (for demo purposes)
        return {
            "address": req.address,
            "balance_eth": 0.0,
            "error": str(e),
            "note": "Failed to connect to blockchain, check RPC URL"
        }

@app.post("/eth/pay")
def process_payment(req: EthPaymentRequest):
    # In a real app, this would verify a signed transaction hash
    # For this demo, we verify the address and simulate success
    if not w3.is_address(req.sender):
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")
        
    return {
        "status": "success",
        "transaction_hash": "0x" + "a" * 64, # Mock hash
        "amount": req.amount,
        "currency": "ETH",
        "service": req.service,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

