FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y curl
RUN apt install -y  python3 python3-pip python3-venv
RUN pip install langchain
RUN pip install streamlit
RUN pip install langchain_community
RUN pip install langchain_experimental
RUN pip install pdfplumber
RUN pip install sentence-transformers
RUN mkdir -p /app
RUN mkdir -p /app/data
COPY data /app/data
EXPOSE 8501
RUN curl -fsSL https://ollama.com/install.sh | sh

RUN pip install hf_xet
RUN pip install faiss-cpu
RUN pip install openai
RUN pip install langchain_openai
RUN pip install fastapi
RUN pip install pydantic
RUN pip install uvicorn
COPY start-api.sh /start-api.sh
RUN chmod +x /start-api.sh
WORKDIR /app
COPY chatbotdoc-ollama-qwen2.5-api.py /app/chatbotdoc.py   
CMD ["/start-api.sh"]