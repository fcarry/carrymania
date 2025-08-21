# Asistente de Voz con IA - Ollama + Coqui TTS

Proyecto de asistente de compañía que implementa un pipeline completo de voz a voz utilizando reconocimiento de voz, Llama en Ollama para procesamiento de lenguaje natural, y Coqui TTS para síntesis de voz.

## 🌟 Características

- 🎤 **Reconocimiento de Voz**: Convierte audio a texto usando SpeechRecognition
- 🧠 **IA Conversacional**: Utiliza Llama 3.2 corriendo en Ollama como asistente de compañía
- 🗣️ **Síntesis de Voz**: Genera respuestas en audio usando Coqui TTS
- 🌐 **Interfaz Web**: Aplicación Streamlit con interfaz intuitiva
- 🔊 **Reproducción Automática**: Reproduce automáticamente las respuestas del asistente
- 💬 **Historial de Chat**: Mantiene conversaciones persistentes durante la sesión
- 📁 **Múltiples Formatos**: Soporta WAV, MP3, OGG, M4A
- 🐳 **Docker**: Completamente containerizado para fácil despliegue

## 🚀 Pipeline de Funcionamiento

```
Audio de Usuario → Reconocimiento de Voz → Texto → Llama/Ollama → Respuesta → Coqui TTS → Audio de Respuesta
```

1. **Captura de Audio**: El usuario sube un archivo de audio o graba directamente
2. **Speech-to-Text**: El audio se transcribe a texto usando reconocimiento de voz
3. **Procesamiento IA**: El texto se envía a Llama 3.2 para generar una respuesta empática
4. **Text-to-Speech**: La respuesta se convierte a audio usando Coqui TTS
5. **Reproducción**: El audio de respuesta se reproduce automáticamente

## 🛠️ Instalación y Uso

### Docker (Recomendado)

```bash
# Construir la imagen
docker build -t voice-assistant-ai .

# Ejecutar el contenedor
docker run -p 8501:8501 voice-assistant-ai
```

### Instalación Local

```bash
# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install ffmpeg espeak espeak-data libespeak-dev
sudo apt-get install portaudio19-dev python3-pyaudio

# Instalar dependencias de Python
pip install streamlit langchain langchain_community requests
pip install SpeechRecognition pyaudio TTS pydub numpy torch torchaudio

# Instalar y configurar Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2

# Ejecutar la aplicación
streamlit run chatbotdoc-voice-assistant-ollama-coqui-web.py
```

## 🖥️ Interfaz de Usuario

La aplicación web incluye:

- **Panel de Estado**: Indicadores de conexión de Ollama, modelo Llama y Coqui TTS
- **Subida de Audio**: Drag & drop para archivos de audio
- **Entrada Manual**: Campo de texto como alternativa a la voz
- **Historial de Chat**: Visualización de conversaciones anteriores
- **Reproductor de Audio**: Reproducción automática de respuestas
- **Controles**: Botones para limpiar conversación y procesar audio

## 📋 Requisitos del Sistema

### Dependencias Python
- streamlit
- langchain
- langchain_community
- requests
- SpeechRecognition
- pyaudio
- TTS (Coqui)
- pydub
- numpy
- torch
- torchaudio

### Dependencias del Sistema
- Python 3.8+
- FFmpeg (para procesamiento de audio)
- Espeak (para TTS)
- PortAudio (para captura de audio)
- Ollama (para LLM)

### Hardware Recomendado
- **RAM**: Mínimo 8GB (16GB recomendado para Llama 3.2)
- **CPU**: Multinúcleo moderno
- **GPU**: Opcional, mejora el rendimiento de TTS y LLM
- **Almacenamiento**: 10GB libre para modelos

## ⚙️ Configuración

### Modelos de IA

- **LLM**: Llama 3.2 (se descarga automáticamente)
- **TTS**: `tts_models/es/css10/vits` (español, se descarga automáticamente)
- **STT**: Google Speech Recognition API (requiere conexión a internet)

### Puertos

- **Streamlit**: 8501
- **Ollama**: 11434 (interno)

## 🎯 Casos de Uso

- **Asistente Personal**: Conversaciones naturales de compañía
- **Accesibilidad**: Interfaz de voz para personas con dificultades motoras
- **Aprendizaje**: Práctica de conversación en español
- **Terapia**: Compañía y conversación empática
- **Prototipos**: Base para desarrollar asistentes de voz especializados

## 🔧 Personalización

### Cambiar el Modelo LLM

Edita la variable `LLAMA_MODEL` en el archivo principal:

```python
LLAMA_MODEL = "llama3.2"  # Cambia por otro modelo disponible
```

### Personalizar el Prompt

Modifica la función `generate_llm_response()` para cambiar el comportamiento del asistente:

```python
prompt = f"""Tu prompt personalizado aquí..."""
```

### Configurar TTS

Cambia el modelo de TTS en la función `text_to_speech()`:

```python
tts = TTS(model_name="tts_models/es/mai/tacotron2-DDC", progress_bar=False)
```

## 🐛 Resolución de Problemas

### Ollama no se conecta
```bash
# Verificar que Ollama esté corriendo
ollama serve

# Verificar modelos disponibles
ollama list
```

### Error de audio/micrófono
```bash
# Instalar dependencias de audio
sudo apt-get install portaudio19-dev python3-pyaudio

# Verificar dispositivos de audio
python -c "import pyaudio; print(pyaudio.PyAudio().get_device_count())"
```

### Coqui TTS no funciona
```bash
# Reinstalar TTS
pip uninstall TTS
pip install TTS

# Verificar modelos disponibles
python -c "from TTS.api import TTS; print(TTS.list_models())"
```

## 📊 Rendimiento

### Tiempos de Respuesta Típicos
- **Transcripción de audio**: 2-5 segundos
- **Generación LLM**: 3-10 segundos (depende del hardware)
- **Síntesis TTS**: 1-3 segundos
- **Total**: 6-18 segundos

### Optimizaciones
- Usar GPU para acelerar TTS y LLM
- Modelos más pequeños para respuestas más rápidas
- Cache de respuestas frecuentes

## 🤝 Contribución

Este proyecto sigue las convenciones del repositorio carrymania:

1. Mantener el estilo de código existente
2. Usar Streamlit para interfaces web
3. Dockerizar todas las aplicaciones
4. Documentar funcionalidades claramente
5. Seguir la paleta de colores establecida

## 📄 Licencia

Apache License 2.0 - Ver archivo LICENSE en el repositorio principal.

## 🙏 Agradecimientos

- **Ollama**: Por facilitar el uso de LLMs localmente
- **Coqui TTS**: Por proporcionar síntesis de voz de código abierto
- **Streamlit**: Por la plataforma de desarrollo web
- **Comunidad de IA**: Por las herramientas y modelos de código abierto

---

*Desarrollado siguiendo los patrones y convenciones del repositorio carrymania para prototipos de IA*