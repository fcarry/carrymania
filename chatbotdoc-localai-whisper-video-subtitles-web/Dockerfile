FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LOCALAI_API_PORT=8080

# Update system and install dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    build-essential \
    git && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages for Streamlit
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org streamlit requests

# Create directories
RUN mkdir -p /app /localai /models

# Download and install LocalAI
WORKDIR /localai
RUN curl -k -Lo local-ai "https://github.com/mudler/LocalAI/releases/latest/download/local-ai-Linux-x86_64" && \
    chmod +x local-ai

# Create LocalAI configuration directory
RUN mkdir -p /localai/models

# Create whisper-base model configuration
RUN echo 'name: whisper-base\n\
backend: whisper\n\
parameters:\n\
  model: base\n\
f16: true\n\
threads: 4' > /localai/models/whisper-base.yaml

# Note: Whisper model will be downloaded automatically by LocalAI on first use
# This avoids network issues during build time

# Expose ports
EXPOSE 8501 8080

# Copy application files
COPY start.sh /start.sh
RUN chmod +x /start.sh

WORKDIR /app
COPY chatbotdoc-localai-whisper-video-subtitles-web.py /app/chatbotdoc.py   

CMD ["/start.sh"]