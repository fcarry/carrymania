#!/bin/bash

# Start LocalAI in the background
echo "Starting LocalAI..."
cd /localai
./local-ai --models-path=/localai/models --address=0.0.0.0:8080 &

# Wait for LocalAI to start
echo "Waiting for LocalAI to initialize..."
sleep 10

# Start Streamlit
echo "Starting Streamlit application..."
streamlit run /app/chatbotdoc.py --server.address=0.0.0.0 --server.port=8501