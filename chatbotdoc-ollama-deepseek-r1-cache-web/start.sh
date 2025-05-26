#!/bin/bash
ollama serve &
sleep 5
ollama pull deepseek-r1  
streamlit run /app/chatbotdoc.py --server.address=0.0.0.0