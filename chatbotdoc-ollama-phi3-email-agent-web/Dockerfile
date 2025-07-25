FROM ubuntu:22.04
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y curl ca-certificates
RUN apt install -y python3 python3-pip python3-venv
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org langchain
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org streamlit
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org langchain_community
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org sentence-transformers
RUN mkdir -p /app
EXPOSE 8501
RUN curl -fsSL https://ollama.com/install.sh | sh

COPY start.sh /start.sh
RUN chmod +x /start.sh
WORKDIR /app
COPY chatbotdoc-ollama-phi3-email-agent-web.py /app/chatbotdoc.py   
CMD ["/start.sh"]