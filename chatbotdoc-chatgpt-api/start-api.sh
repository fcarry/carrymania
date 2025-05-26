#!/bin/bash
cd /app
uvicorn chatbotdoc:app --host 0.0.0.0 --port 8501