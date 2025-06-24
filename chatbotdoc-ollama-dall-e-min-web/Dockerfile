FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt install -y  python3 python3-pip python3-venv
RUN mkdir -p /app
EXPOSE 8501
RUN pip install streamlit
RUN pip install diffusers 
RUN pip install accelerate 
RUN pip install torch
RUN apt install -y git 
RUN pip install git+https://github.com/huggingface/transformers.git
COPY start.sh /start.sh
RUN chmod +x /start.sh
WORKDIR /app
COPY chatbotdoc-dall-e-min-web.py /app/chatbotdoc.py   
CMD ["/start.sh"]