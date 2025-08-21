import streamlit as st
import tempfile
import os
import requests
import json
import base64
from io import BytesIO
import time
import threading
from pathlib import Path

# Try to import optional dependencies
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False
    st.info("📝 SpeechRecognition no disponible. Se habilitará entrada de texto manual.")

try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    st.info("🔊 Coqui TTS no disponible. Solo respuestas de texto.")

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
    .demo-section {{
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid {primary_color};
        margin: 20px 0;
    }}
    </style>
""", unsafe_allow_html=True)

def check_ollama_health():
    """Check if Ollama is running and healthy"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_llama_model():
    """Check if Llama model is available"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return any(LLAMA_MODEL in model.get('name', '') for model in models)
        return False
    except:
        return False

def simulate_llm_response(text):
    """Simulate LLM response when Ollama is not available"""
    responses = {
        "hola": "¡Hola! Estoy muy bien, gracias por preguntar. Es un placer poder conversar contigo hoy. ¿En qué puedo ayudarte?",
        "chiste": "¡Por supuesto! ¿Por qué los pájaros vuelan hacia el sur en invierno? ¡Porque es demasiado lejos para caminar! 😄",
        "cocina": "¡Me encanta cocinar! ¿Qué tipo de plato te gustaría preparar? Puedo sugerirte desde una pasta sencilla hasta algo más elaborado.",
        "tiempo": "Lo siento, no tengo acceso a información del tiempo en tiempo real, pero espero que tengas un día hermoso. ¿Hay algo más en lo que pueda ayudarte?",
        "historia": "Había una vez un pequeño robot que soñaba con hacer amigos. Un día conoció a una persona muy amable que le enseñó que la amistad se construye con conversaciones como esta. ¡Fin!",
        "ayuda": "Estoy aquí para ser tu compañía y ayudarte con lo que necesites. Puedes preguntarme cualquier cosa o simplemente conversar conmigo.",
        "como estas": "¡Estoy excelente! Me emociona mucho poder conversar contigo. Cada conversación es una nueva aventura para mí."
    }
    
    for keyword, response in responses.items():
        if keyword in text.lower():
            return response
    
    return f"Es muy interesante lo que me dices: '{text}'. Me encanta poder conversar contigo. ¿Hay algo específico en lo que pueda ayudarte?"

def generate_llm_response(text):
    """Generate response using Ollama Llama model or simulation"""
    if check_ollama_health():
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
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Lo siento, no pude generar una respuesta.')
            else:
                return simulate_llm_response(text)
        except Exception as e:
            return simulate_llm_response(text)
    else:
        return simulate_llm_response(text)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

# Main app
st.title("🎤 Asistente de Voz con IA")
st.markdown("Asistente de compañía que convierte voz a texto, procesa con Llama en Ollama y responde con voz usando Coqui TTS")

# Status indicators
col1, col2, col3 = st.columns(3)

with col1:
    if check_ollama_health():
        st.success("✅ Ollama conectado")
    else:
        st.warning("⚠️ Ollama desconectado (modo demo)")

with col2:
    if check_llama_model():
        st.success(f"✅ Modelo {LLAMA_MODEL} disponible")
    else:
        st.info(f"ℹ️ Modo simulado (sin {LLAMA_MODEL})")

with col3:
    if HAS_TTS:
        st.success("✅ Coqui TTS disponible")
    else:
        st.info("ℹ️ TTS simulado")

# Demo mode notification
if not check_ollama_health() or not HAS_SPEECH_RECOGNITION or not HAS_TTS:
    st.markdown(f"""
    <div class="demo-section">
        <h4>🚀 Modo Demostración</h4>
        <p>Esta aplicación está funcionando en modo demo. En un entorno completo tendríamos:</p>
        <ul>
            <li>🎤 <strong>Reconocimiento de voz</strong> para procesar archivos de audio</li>
            <li>🧠 <strong>Ollama + Llama 3.2</strong> para procesamiento de lenguaje natural</li>
            <li>🗣️ <strong>Coqui TTS</strong> para síntesis de voz en español</li>
            <li>🔊 <strong>Reproducción automática</strong> de respuestas de audio</li>
        </ul>
        <p>Por ahora puedes probar la funcionalidad con entrada de texto manual.</p>
    </div>
    """, unsafe_allow_html=True)

# Audio upload section (demo)
st.markdown("### 🎙️ Carga de Audio")
uploaded_audio = st.file_uploader(
    "Sube un archivo de audio (demo)",
    type=['wav', 'mp3', 'ogg', 'm4a'],
    help="En la versión completa, esto procesaría el audio automáticamente"
)

if uploaded_audio is not None:
    st.audio(uploaded_audio, format='audio/wav')
    if st.button("🎤 Procesar Audio (Demo)"):
        st.info("📝 En la versión completa, aquí se transcribiría automáticamente el audio a texto")
        st.success("🔊 Luego se reproduciría la respuesta en audio automáticamente")

# Manual text input
st.markdown("### ✍️ Entrada de Texto")
manual_text = st.text_input("Escribe tu mensaje:", placeholder="Ej: Hola, ¿cómo estás?")

if manual_text and st.button("📤 Enviar Mensaje"):
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": manual_text})
    
    with st.spinner("🧠 Generando respuesta..."):
        time.sleep(1)  # Simulate processing
        llm_response = generate_llm_response(manual_text)
    
    st.session_state.chat_history.append({"role": "assistant", "content": llm_response})
    
    if HAS_TTS:
        st.info("🔊 En la versión completa, esta respuesta se convertiría a audio automáticamente")
    
    st.rerun()

# Sample conversations
st.markdown("### 💬 Conversaciones de Ejemplo")
sample_prompts = [
    "Hola, ¿cómo estás?",
    "¿Puedes contarme un chiste?",
    "Cuéntame una historia corta",
    "¿Me ayudas con una receta?",
    "¿Cómo te encuentras hoy?"
]

cols = st.columns(len(sample_prompts))
for i, prompt in enumerate(sample_prompts):
    with cols[i]:
        if st.button(f"💭 '{prompt[:15]}...'", key=f"sample_{i}"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = generate_llm_response(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
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
### ℹ️ Cómo funciona el asistente completo:

1. **📤 Subir Audio**: El usuario sube un archivo de audio con su voz
2. **🎤 Transcripción**: El audio se convierte a texto usando SpeechRecognition
3. **🧠 IA**: El texto se envía a Llama 3.2 corriendo en Ollama para generar respuesta empática
4. **🔊 TTS**: La respuesta se convierte a voz usando Coqui TTS en español
5. **▶️ Reproducción**: El audio de respuesta se reproduce automáticamente

### 🔧 Tecnologías del Pipeline Completo:
- **Streamlit**: Interfaz web interactiva
- **SpeechRecognition**: Conversión de voz a texto (Google API)
- **Ollama + Llama 3.2**: Procesamiento de lenguaje natural local
- **Coqui TTS**: Síntesis de voz en español de código abierto
- **Docker**: Despliegue containerizado con todas las dependencias

### 🚀 Para desplegar la versión completa:
```bash
docker build -t voice-assistant .
docker run -p 8501:8501 voice-assistant
```

### 🎯 Casos de Uso:
- **Compañía**: Conversaciones naturales y empáticas
- **Accesibilidad**: Interfaz de voz para personas con dificultades motoras  
- **Aprendizaje**: Práctica de conversación en español
- **Terapia**: Apoyo emocional y conversación de compañía
""")

# Footer
st.markdown("---")
st.markdown("*🤖 Desarrollado siguiendo los patrones del repositorio carrymania para prototipos de IA*")