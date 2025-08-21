#!/bin/bash

# Start Ollama service in background
ollama serve &

# Wait for Ollama to be ready
sleep 10

# Pull the Llama model
echo "Pulling Llama 3.2 model..."
ollama pull llama3.2

# Start Streamlit application
echo "Starting Voice Assistant application..."
streamlit run /app/chatbotdoc.py --server.address=0.0.0.0 --server.port=8501