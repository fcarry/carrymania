#!/bin/bash
ollama serve &
sleep 5
ollama pull deepseek-r1  
cd /app
uvicorn chatbotdoc:app --host 0.0.0.0 --port 8501