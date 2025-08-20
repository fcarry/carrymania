FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y curl python3 python3-pip python3-venv \
    ffmpeg espeak espeak-data libespeak-dev \
    portaudio19-dev python3-pyaudio \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    streamlit \
    langchain \
    langchain_community \
    requests \
    SpeechRecognition \
    pyaudio \
    TTS \
    pydub \
    numpy \
    torch \
    torchaudio

# Create app directory
RUN mkdir -p /app

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy application files
COPY start.sh /start.sh
RUN chmod +x /start.sh

WORKDIR /app
COPY chatbotdoc-voice-assistant-ollama-coqui-web.py /app/chatbotdoc.py

# Expose Streamlit port
EXPOSE 8501

# Set default command
CMD ["/start.sh"]