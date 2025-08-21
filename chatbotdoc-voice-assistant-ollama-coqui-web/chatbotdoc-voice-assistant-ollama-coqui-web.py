import streamlit as st
import speech_recognition as sr
import tempfile
import os
import requests
import json
import base64
from io import BytesIO
import time
import threading
from pathlib import Path

# Try to import TTS, fallback if not available
try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    st.warning("⚠️ Coqui TTS not available. Install with: pip install TTS")

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
LLAMA_MODEL = "llama3.2"

# Color palette (following existing project style)
primary_color = "#1E90FF"
secondary_color = "#FF6347"
background_color = "#F5F5F5"
text_color = "#4561e9"
success_color = "#28a745"
warning_color = "#ffc107"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        margin: 5px;
    }}
    .record-button {{
        background-color: {secondary_color} !important;
        font-weight: bold;
    }}
    .stop-button {{
        background-color: {warning_color} !important;
        color: black !important;
    }}
    .chat-message {{
        padding: 10px;
        margin: 10px 0;
        border-radius: 10px;
        max-width: 80%;
    }}
    .user-message {{
        background-color: {primary_color};
        color: white;
        margin-left: auto;
        text-align: right;
    }}
    .assistant-message {{
        background-color: white;
        color: {text_color};
        border: 1px solid {primary_color};
    }}
    .audio-controls {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }}
    .status-indicator {{
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }}
    .status-recording {{
        background-color: {secondary_color};
        color: white;
    }}
    .status-processing {{
        background-color: {warning_color};
        color: black;
    }}
    .status-ready {{
        background-color: {success_color};
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

def check_ollama_health():
    """Check if Ollama is running and healthy"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_llama_model():
    """Check if Llama model is available"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return any(LLAMA_MODEL in model.get('name', '') for model in models)
        return False
    except:
        return False

def generate_llm_response(text):
    """Generate response using Ollama Llama model"""
    try:
        prompt = f"""Eres un asistente de compañía amigable y útil. Responde de manera concisa, empática y natural. 
        La persona te ha dicho: "{text}"
        
        Responde en español de manera conversacional y cálida, como si fueras un amigo cercano."""
        
        payload = {
            "model": LLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 150
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Lo siento, no pude generar una respuesta.')
        else:
            return f"Error al conectar con el modelo: {response.status_code}"
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

def transcribe_audio(audio_file_path):
    """Transcribe audio file to text using speech recognition"""
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)
        
        # Try to recognize speech using Google's speech recognition
        try:
            text = recognizer.recognize_google(audio, language='es-ES')
            return text
        except sr.UnknownValueError:
            return "No se pudo entender el audio"
        except sr.RequestError as e:
            return f"Error en el servicio de reconocimiento: {e}"
            
    except Exception as e:
        return f"Error al procesar el audio: {str(e)}"

def text_to_speech(text, output_path):
    """Convert text to speech using Coqui TTS"""
    if not HAS_TTS:
        return False, "Coqui TTS no está disponible"
    
    try:
        # Initialize TTS with Spanish model
        tts = TTS(model_name="tts_models/es/css10/vits", progress_bar=False)
        
        # Generate speech
        tts.tts_to_file(text=text, file_path=output_path)
        return True, "Audio generado exitosamente"
    except Exception as e:
        return False, f"Error al generar audio: {str(e)}"

def create_audio_player(audio_file_path):
    """Create HTML audio player for the generated speech"""
    try:
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        audio_html = f"""
        <audio controls autoplay style="width: 100%;">
            <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            Tu navegador no soporta audio HTML5.
        </audio>
        """
        return audio_html
    except Exception as e:
        st.error(f"Error al crear reproductor de audio: {str(e)}")
        return None

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'is_recording' not in st.session_state:
    st.session_state.is_recording = False
if 'status' not in st.session_state:
    st.session_state.status = "ready"

# Main app
st.title("🎤 Asistente de Voz con IA")
st.markdown("Asistente de compañía que convierte voz a texto, procesa con Llama en Ollama y responde con voz usando Coqui TTS")

# Status indicators
col1, col2, col3 = st.columns(3)

with col1:
    if check_ollama_health():
        st.success("✅ Ollama conectado")
    else:
        st.error("❌ Ollama desconectado")

with col2:
    if check_llama_model():
        st.success(f"✅ Modelo {LLAMA_MODEL} disponible")
    else:
        st.warning(f"⚠️ Modelo {LLAMA_MODEL} no encontrado")

with col3:
    if HAS_TTS:
        st.success("✅ Coqui TTS disponible")
    else:
        st.error("❌ Coqui TTS no disponible")

# Current status
status_text = {
    "ready": "🟢 Listo para grabar",
    "recording": "🔴 Grabando...",
    "processing": "🟡 Procesando...",
    "generating": "🟡 Generando respuesta...",
    "speaking": "🔊 Reproduciendo respuesta"
}

current_status = st.session_state.get('status', 'ready')
st.markdown(f"""
<div class="status-indicator status-{current_status.replace('generating', 'processing').replace('speaking', 'ready')}">
    {status_text.get(current_status, '🟢 Listo')}
</div>
""", unsafe_allow_html=True)

# Audio recording interface
st.markdown("### 🎙️ Control de Audio")

col1, col2 = st.columns(2)

# File uploader for audio input (alternative to recording)
uploaded_audio = st.file_uploader(
    "O sube un archivo de audio",
    type=['wav', 'mp3', 'ogg', 'm4a'],
    help="Formatos soportados: WAV, MP3, OGG, M4A"
)

if uploaded_audio is not None:
    if st.button("🎤 Procesar Audio Subido"):
        st.session_state.status = "processing"
        st.rerun()
        
        with st.spinner("Procesando audio..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(uploaded_audio.read())
                temp_audio_path = temp_audio.name
            
            try:
                # Step 1: Transcribe audio
                with st.spinner("🎤 Transcribiendo audio..."):
                    transcribed_text = transcribe_audio(temp_audio_path)
                
                if transcribed_text and "Error" not in transcribed_text and "No se pudo" not in transcribed_text:
                    st.session_state.chat_history.append({"role": "user", "content": transcribed_text})
                    
                    # Step 2: Generate LLM response
                    st.session_state.status = "generating"
                    with st.spinner("🧠 Generando respuesta con IA..."):
                        llm_response = generate_llm_response(transcribed_text)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": llm_response})
                    
                    # Step 3: Convert to speech
                    if HAS_TTS:
                        st.session_state.status = "speaking"
                        with st.spinner("🔊 Generando audio de respuesta..."):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_tts:
                                tts_path = temp_tts.name
                            
                            success, message = text_to_speech(llm_response, tts_path)
                            
                            if success:
                                audio_html = create_audio_player(tts_path)
                                if audio_html:
                                    st.markdown("### 🔊 Respuesta de Audio")
                                    st.markdown(audio_html, unsafe_allow_html=True)
                            else:
                                st.error(f"Error al generar audio: {message}")
                            
                            # Cleanup TTS file
                            try:
                                os.unlink(tts_path)
                            except:
                                pass
                    else:
                        st.info("💬 Audio TTS no disponible, solo respuesta de texto")
                    
                    st.session_state.status = "ready"
                else:
                    st.error(f"Error en transcripción: {transcribed_text}")
                    st.session_state.status = "ready"
                
            finally:
                # Cleanup uploaded file
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass

# Manual text input as alternative
st.markdown("### ✍️ Entrada de Texto Manual")
manual_text = st.text_input("O escribe tu mensaje directamente:")

if manual_text and st.button("📤 Enviar Texto"):
    st.session_state.status = "generating"
    
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": manual_text})
    
    with st.spinner("🧠 Generando respuesta..."):
        llm_response = generate_llm_response(manual_text)
    
    st.session_state.chat_history.append({"role": "assistant", "content": llm_response})
    
    # Convert to speech
    if HAS_TTS:
        st.session_state.status = "speaking"
        with st.spinner("🔊 Generando audio..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_tts:
                tts_path = temp_tts.name
            
            success, message = text_to_speech(llm_response, tts_path)
            
            if success:
                audio_html = create_audio_player(tts_path)
                if audio_html:
                    st.markdown("### 🔊 Respuesta de Audio")
                    st.markdown(audio_html, unsafe_allow_html=True)
            
            # Cleanup
            try:
                os.unlink(tts_path)
            except:
                pass
    
    st.session_state.status = "ready"
    st.rerun()

# Chat history
if st.session_state.chat_history:
    st.markdown("### 💬 Historial de Conversación")
    
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 Tú:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Asistente:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)

# Clear chat button
if st.session_state.chat_history:
    if st.button("🗑️ Limpiar Conversación"):
        st.session_state.chat_history = []
        st.rerun()

# Information section
st.markdown("---")
st.markdown("""
### ℹ️ Cómo funciona:

1. **📤 Subir Audio**: Selecciona un archivo de audio con tu voz
2. **🎤 Transcripción**: El audio se convierte a texto usando reconocimiento de voz
3. **🧠 IA**: El texto se envía a Llama corriendo en Ollama para generar respuesta
4. **🔊 TTS**: La respuesta se convierte a voz usando Coqui TTS
5. **▶️ Reproducción**: El audio de respuesta se reproduce automáticamente

### 🔧 Tecnologías:
- **Streamlit**: Interfaz web interactiva
- **Speech Recognition**: Conversión de voz a texto
- **Ollama + Llama**: Procesamiento de lenguaje natural
- **Coqui TTS**: Síntesis de voz en español
- **Docker**: Despliegue containerizado

### 📝 Formatos de Audio Soportados:
- WAV (recomendado)
- MP3
- OGG
- M4A

### 🎯 Consejos para mejor calidad:
- Habla claramente y a velocidad normal
- Usa un micrófono de buena calidad
- Graba en un ambiente silencioso
- Mantén una distancia apropiada del micrófono
""")