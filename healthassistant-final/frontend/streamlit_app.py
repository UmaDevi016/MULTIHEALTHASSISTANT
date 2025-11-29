# streamlit_app.py - Beautiful Multilingual Health Assistant with Voice
import streamlit as st
import requests
import os
import traceback
from dotenv import load_dotenv
import tempfile
import base64

# Try to import voice libraries
try:
    from streamlit_mic_recorder import mic_recorder
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


load_dotenv()

# Default backend URL
DEFAULT_BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration with custom theme
st.set_page_config(
    page_title="🏥 Multilingual Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom card styling */
    .custom-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Success message styling */
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 500;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    
    /* Reminder card */
    .reminder-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 6px solid #667eea;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .reminder-card h4 {
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .reminder-card p {
        color: #4a5568;
        font-size: 1.1rem;
        margin: 0.2rem 0;
    }
    
    .reminder-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        background: #ffffff;
    }
    
    /* Voice recording indicator */
    .recording-indicator {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        margin: 1rem 0;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "backend_url" not in st.session_state:
    st.session_state.backend_url = DEFAULT_BACKEND
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "last_translation" not in st.session_state:
    st.session_state.last_translation = ""
if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = ""
if "tts_audio_bytes" not in st.session_state:
    st.session_state.tts_audio_bytes = None


BACKEND = st.session_state.backend_url.rstrip("/")

# Language mappings
languages = {
    "🇮🇳 Hindi": "hi",
    "🇮🇳 Tamil": "ta",
    "🇮🇳 Telugu": "te",
    "🇮🇳 Bengali": "bn",
    "🇮🇳 Malayalam": "ml",
    "🇮🇳 Marathi": "mr",
    "🇮🇳 Odia": "or",
    "🇪🇸 Spanish": "es",
    "🇫🇷 French": "fr",
    "🇸🇦 Arabic": "ar",
    "🇬🇧 English": "en"
}

# Speech recognition language codes
speech_lang_codes = {
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "bn": "bn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "or": "or-IN",
    "es": "es-ES",
    "fr": "fr-FR",
    "ar": "ar-SA",
    "en": "en-US"
}

# gTTS language codes (ISO 639-1)
gtts_lang_codes = {
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    "bn": "bn",
    "ml": "ml",
    "mr": "mr",
    "or": "en", # Odia not supported by gTTS, fallback to English
    "es": "es",
    "fr": "fr",
    "ar": "ar",
    "en": "en"
}

# Confirmation messages
confirmation_msgs = {
    "hi": "दवा का रिमांडर सेट किया गया: {medicine} समय {time}",
    "ta": "மருந்து நினைவூட்டல் சேர்க்கப்பட்டது: {medicine} நேரம் {time}",
    "te": "మందుల రిమైండర్ జోడించబడింది: {medicine} సమయం {time}",
    "bn": "ওষুধের রিমাইন্ডার যোগ করা হয়েছে: {medicine} সময় {time}",
    "ml": "മരുന്ന് ഓർമ്മപ്പെടുത്തൽ ചേർത്തു: {medicine} സമയം {time}",
    "mr": "औषध स्मरणपत्र जोडले: {medicine} वेळ {time}",
    "or": "Medicine reminder added: {medicine} at {time}",
    "es": "Recordatorio de medicina añadido: {medicine} a las {time}",
    "fr": "Rappel de médicament ajouté : {medicine} à {time}",
    "ar": "تم إضافة تذكير الدواء: {medicine} في {time}",
    "en": "Reminder added for {medicine} at {time}"
}

# Function to convert audio to text
def audio_to_text(audio_bytes, language="en-US"):
    """Convert audio bytes to text using speech recognition with pydub conversion"""
    if not SR_AVAILABLE:
        return None, "Speech recognition library not available"
    
    try:
        # Save raw audio bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
            
        # Convert to compatible WAV using pydub if available
        wav_path = tmp_file_path
        if PYDUB_AVAILABLE:
            try:
                audio = AudioSegment.from_file(tmp_file_path)
                # Export as PCM WAV (required by SpeechRecognition)
                wav_path = tmp_file_path + "_converted.wav"
                audio.export(wav_path, format="wav")
            except Exception as e:
                print(f"Pydub conversion error: {e}")
                # Fallback to original file
                wav_path = tmp_file_path

        recognizer = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(wav_path) as source:
            # Adjust for ambient noise to improve accuracy
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        
        # Recognize speech
        print(f"Recognizing speech for language: {language}")
        text = recognizer.recognize_google(audio_data, language=language)
        print(f"Recognized text: {text}")
        
        # Clean up temp files
        try:
            os.unlink(tmp_file_path)
            if wav_path != tmp_file_path:
                os.unlink(wav_path)
        except:
            pass
        
        return text, None
    except sr.UnknownValueError:
        return None, "Could not understand audio. Please speak clearly."
    except sr.RequestError as e:
        print(f"Speech recognition request error: {e}")
        return None, f"Speech service error: {e}"
    except Exception as e:
        print(f"General speech error: {e}")
        return None, f"Error: {str(e)}"

# Function to create audio from text
def text_to_audio(text, lang="en"):
    """Convert text to speech using gTTS"""
    if not GTTS_AVAILABLE:
        return None
    
    try:
        print(f"Generating TTS for: {text[:20]}... in {lang}")
        # Map 'or' (Odia) to 'en' fallback if not supported, or try 'bn' (Bengali) as close alternative if needed
        # gTTS might throw error for unsupported codes
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                tmp_file_path = tmp_file.name
        except ValueError as ve:
            print(f"Language {lang} not supported by gTTS: {ve}")
            return None
            
        # Read audio file
        with open(tmp_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Clean up
        os.unlink(tmp_file_path)
        
        return audio_bytes
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        st.error(f"Text-to-speech error: {e}")
        return None

# Header
st.markdown('<h1 class="main-header">🏥 Multilingual Health Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">🎤 Voice-Enabled • Breaking language barriers in healthcare • Empowering elderly care worldwide</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Voice toggle
    st.session_state.voice_enabled = st.toggle("🎤 Enable Voice Features", value=True)
    
    # Backend URL configuration
    with st.expander("🔧 Backend Configuration", expanded=False):
        backend_input = st.text_input("Backend URL", value=st.session_state.backend_url, key="backend_input")
        if st.button("Apply Changes"):
            st.session_state.backend_url = backend_input
            st.success("✅ Backend URL updated!")
    
    # Health check
    st.markdown("### 📊 System Status")
    try:
        resp = requests.get(f"{BACKEND}/health", timeout=6)
        if resp.ok:
            st.success("🟢 Backend Online")
            with st.expander("View Details"):
                st.json(resp.json())
        else:
            st.error(f"🔴 Backend Error: {resp.status_code}")
    except Exception as e:
        st.error("🔴 Backend Offline")
        with st.expander("View Error"):
            st.code(traceback.format_exc(), language="python")
    
    # Voice status
    if st.session_state.voice_enabled:
        st.markdown("### 🎤 Voice Status")
        if MIC_AVAILABLE and SR_AVAILABLE and GTTS_AVAILABLE:
            st.success("🟢 All voice features available")
        else:
            st.warning("⚠️ Some voice features unavailable")
            if not MIC_AVAILABLE:
                st.caption("❌ Microphone recorder")
            if not SR_AVAILABLE:
                st.caption("❌ Speech recognition")
            if not GTTS_AVAILABLE:
                st.caption("❌ Text-to-speech")
    
    # Language info
    st.markdown("### 🌍 Supported Languages")
    for lang_name in languages.keys():
        st.markdown(f"• {lang_name}")

# Main content area
tab1, tab2, tab3 = st.tabs(["🌐 Translate", "💊 Reminders", "💎 Health Wallet"])

# Translation Section
with tab1:
    st.markdown("### 🌐 Translate Health Messages")
    
    with st.container():
        # Language selection
        lang_display = st.selectbox(
            "Select target language",
            options=list(languages.keys()),
            index=0,
            help="Choose the language you want to translate to",
            key="lang_select"
        )
        lang = languages[lang_display]
        speech_lang = speech_lang_codes.get(lang, "en-US")
        
        # Voice input section
        if st.session_state.voice_enabled and MIC_AVAILABLE and SR_AVAILABLE:
            st.markdown("#### 🎙️ Voice Input")
            st.info("Click the microphone button below, speak your message, then click stop when done.")
            
            # Microphone recorder
            audio_data = mic_recorder(
                start_prompt="🎤 Start Recording",
                stop_prompt="⏹️ Stop Recording",
                just_once=False,
                use_container_width=True,
                key="voice_recorder"
            )
            
            if audio_data is not None:
                # Playback recorded audio for verification
                st.audio(audio_data['bytes'], format="audio/wav")
                
                st.markdown('<div class="recording-indicator">🎙️ Processing your voice...</div>', unsafe_allow_html=True)

                
                # Convert audio to text
                audio_bytes = audio_data['bytes']
                recognized_text, error = audio_to_text(audio_bytes, speech_lang)
                
                if recognized_text:
                    st.session_state.recognized_text = recognized_text
                    st.success(f"✅ Recognized: {recognized_text}")
                elif error:
                    st.error(f"❌ {error}")
            
            st.markdown("---")
        
        # Text input
        default_text = st.session_state.recognized_text if st.session_state.recognized_text else ""
        txt = st.text_area(
            "Enter your health message (or use voice input above)",
            value=default_text,
            placeholder="e.g., Take your medicine after breakfast",
            height=150,
            help="Enter a health-related message to translate or use the microphone",
            key="message_input"
        )
        
        # Translate button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            translate_btn = st.button("🔄 Translate Now", use_container_width=True)
        
        if translate_btn:
            if not txt.strip():
                st.warning("⚠️ Please enter a message to translate or use voice input")
            else:
                with st.spinner("🔄 Translating your message..."):
                    try:
                        resp = requests.post(
                            f"{BACKEND}/translate",
                            json={"text": txt, "target_lang": lang},
                            timeout=12
                        )
                        if resp.ok:
                            data = resp.json()
                            translated = data.get("translated_text") or data.get("translation") or ""
                            if translated:
                                st.session_state.last_translation = translated
                                # Reset audio when new translation happens
                                st.session_state.tts_audio_bytes = None
                            else:
                                st.warning("⚠️ Translation returned empty")
                        else:
                            st.error(f"❌ Translation failed: {resp.status_code}")
                    except Exception as e:
                        st.error("❌ Connection error. Please check if the backend is running.")
                        with st.expander("View error details"):
                            st.code(traceback.format_exc(), language="python")

        # Always display translation result if available
        if st.session_state.last_translation:
            st.markdown(f'<div class="success-box">✨ Translation: <br><strong style="font-size: 1.4rem;">{st.session_state.last_translation}</strong></div>', unsafe_allow_html=True)
            
            # Voice output
            if st.session_state.voice_enabled and GTTS_AVAILABLE:
                col_speak1, col_speak2, col_speak3 = st.columns([1, 2, 1])
                with col_speak2:
                    if st.button("🔊 Listen to Translation", use_container_width=True, key="voice_output"):
                        # Use correct gTTS code
                        tts_lang = gtts_lang_codes.get(lang, "en")
                        audio_bytes = text_to_audio(st.session_state.last_translation, tts_lang)
                        if audio_bytes:
                            st.session_state.tts_audio_bytes = audio_bytes
                            
                    # Play from session state if available
                    if st.session_state.tts_audio_bytes:
                        st.audio(st.session_state.tts_audio_bytes, format="audio/mp3")
                        st.success("🔊 Audio Ready")

# Reminders Section
with tab2:
    st.markdown("### 💊 Medicine Reminders")
    
    with st.form("add_reminder_form", clear_on_submit=True):
        medicine = st.text_input(
            "💊 Medicine Name",
            placeholder="e.g., Aspirin",
            help="Enter the name of the medicine"
        )
        dosage = st.text_input(
            "📏 Dosage",
            placeholder="e.g., 1 tablet",
            help="Specify the dosage amount"
        )
        time = st.text_input(
            "⏰ Time",
            placeholder="e.g., 09:00 AM",
            help="When should the medicine be taken?"
        )
        
        col_form1, col_form2, col_form3 = st.columns([1, 2, 1])
        with col_form2:
            submitted = st.form_submit_button("➕ Add Reminder", use_container_width=True)
        
        if submitted:
            if not medicine.strip():
                st.warning("⚠️ Please enter medicine name")
            else:
                try:
                    r = requests.post(
                        f"{BACKEND}/add-reminder",
                        json={
                            "medicine": medicine,
                            "dosage": dosage,
                            "time": time,
                            "language": "en"
                        },
                        timeout=8
                    )
                    if r.ok:
                        st.success("✅ Reminder added successfully!")
                        
                        # Voice confirmation
                        if st.session_state.voice_enabled and GTTS_AVAILABLE:
                            # Get message in selected language (from translation tab)
                            # We use the 'lang' variable from the translation tab which holds the current selected language
                            current_lang = lang 
                            tts_lang = gtts_lang_codes.get(current_lang, "en")
                            
                            # Format message
                            msg_template = confirmation_msgs.get(current_lang, confirmation_msgs["en"])
                            confirmation_text = msg_template.format(medicine=medicine, time=time)
                            
                            audio_bytes = text_to_audio(confirmation_text, tts_lang)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                        
                        st.balloons()
                    else:
                        st.error(f"❌ Failed to add reminder: {r.status_code}")
                except Exception as e:
                    st.error("❌ Connection error")
                    with st.expander("View error details"):
                        st.code(traceback.format_exc(), language="python")
    
    st.markdown("---")
    
    # Load reminders button
    col_load1, col_load2, col_load3 = st.columns([1, 2, 1])
    with col_load2:
        if st.button("📋 View All Reminders", use_container_width=True):
            try:
                r = requests.get(f"{BACKEND}/reminders", timeout=8)
                if r.ok:
                    data = r.json().get("reminders", [])
                    if not data:
                        st.info("📭 No reminders found. Add your first reminder above!")
                    else:
                        st.markdown(f"### 📋 Your Reminders ({len(data)})")
                        for idx, rem in enumerate(data, 1):
                            st.markdown(f"""
                            <div class="reminder-card">
                                <h4>💊 {rem.get('medicine', 'N/A')}</h4>
                                <p><strong>📏 Dosage:</strong> {rem.get('dosage', 'N/A')}</p>
                                <p><strong>⏰ Time:</strong> {rem.get('time', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Failed to load reminders: {r.status_code}")
            except Exception as e:
                st.error("❌ Connection error")
                with st.expander("View error details"):
                    st.code(traceback.format_exc(), language="python")

# Health Wallet Section
with tab3:
    st.markdown("### 💎 Health Wallet (Ethereum)")
    st.info("Connect your Ethereum wallet to pay for premium health services.")
    
    wallet_addr = st.text_input("🔑 Enter Ethereum Address", placeholder="0x...", help="Enter your public ETH address")
    
    if wallet_addr:
        if st.button("🔍 Check Balance"):
            try:
                r = requests.post(f"{BACKEND}/eth/balance", json={"address": wallet_addr}, timeout=10)
                if r.ok:
                    data = r.json()
                    if "error" in data:
                        st.warning(f"⚠️ Could not fetch real balance: {data['error']}")
                        st.caption("Using demo mode")
                    
                    eth_bal = data.get("balance_eth", 0.0)
                    st.metric("ETH Balance", f"{eth_bal:.4f} ETH")
                    
                    if eth_bal > 0:
                        st.success("✅ Wallet Connected")
                    else:
                        st.warning("⚠️ Low Balance")
                else:
                    st.error(f"Error: {r.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    st.markdown("#### 🏥 Premium Services")
    
    col_srv1, col_srv2 = st.columns(2)
    
    with col_srv1:
        st.markdown("""
        <div class="custom-card">
            <h4>👨‍⚕️ Tele-Consultation</h4>
            <p>Video call with a specialist</p>
            <h3>0.05 ETH</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Pay 0.05 ETH", key="pay_consult"):
            if not wallet_addr:
                st.error("Please enter wallet address first")
            else:
                with st.spinner("Processing transaction..."):
                    try:
                        r = requests.post(f"{BACKEND}/eth/pay", json={
                            "sender": wallet_addr,
                            "amount": 0.05,
                            "service": "Tele-Consultation"
                        })
                        if r.ok:
                            st.balloons()
                            st.success("✅ Payment Successful! Doctor will join shortly.")
                            st.json(r.json())
                        else:
                            st.error(f"Payment failed: {r.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col_srv2:
        st.markdown("""
        <div class="custom-card">
            <h4>📑 Health Report</h4>
            <p>AI analysis of your records</p>
            <h3>0.01 ETH</h3>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Pay 0.01 ETH", key="pay_report"):
            if not wallet_addr:
                st.error("Please enter wallet address first")
            else:
                with st.spinner("Processing transaction..."):
                    try:
                        r = requests.post(f"{BACKEND}/eth/pay", json={
                            "sender": wallet_addr,
                            "amount": 0.01,
                            "service": "Health Report"
                        })
                        if r.ok:
                            st.balloons()
                            st.success("✅ Payment Successful! Report generating...")
                            st.json(r.json())
                        else:
                            st.error(f"Payment failed: {r.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem;">
    <p style="font-size: 1.1rem; font-weight: 500;">
        Made with ❤️ for elderly care • 🎤 Voice-Enabled • Breaking language barriers in healthcare
    </p>
    <p style="font-size: 0.9rem; opacity: 0.8;">
        Powered by Google Translate, gTTS & FastAPI • Supporting 8 languages worldwide
    </p>
</div>
""", unsafe_allow_html=True)
