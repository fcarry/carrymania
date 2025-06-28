FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt install -y  python3 python3-pip python3-venv
RUN apt -y install ffmpeg
RUN mkdir -p /app
EXPOSE 8501
RUN pip install streamlit
RUN pip install openai-whisper ffmpeg-python
COPY start.sh /start.sh
RUN chmod +x /start.sh
WORKDIR /app
COPY chatbotdoc-extract-text-from-video.py /app/chatbotdoc.py   
CMD ["/start.sh"]