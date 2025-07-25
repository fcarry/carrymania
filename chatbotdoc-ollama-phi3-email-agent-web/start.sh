#!/bin/bash
ollama serve &
sleep 5
ollama pull phi3  
streamlit run /app/chatbotdoc.py --server.address=0.0.0.0