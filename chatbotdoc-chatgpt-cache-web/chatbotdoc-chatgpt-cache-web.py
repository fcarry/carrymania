import streamlit as st
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import os

os.environ["OPENAI_API_KEY"] = "APY_KEY_HERE"  # Replace with your actual OpenAI API key
# color palette
primary_color = "#1E90FF"
secondary_color = "#FF6347"
background_color = "#F5F5F5"
text_color = "#4561e9"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }}
    .stTextInput>div>div>input {{
        border: 2px solid {primary_color};
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }}
    .stFileUploader>div>div>div>button {{
        background-color: {secondary_color};
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }}
    </style>
""", unsafe_allow_html=True)

# Streamlit app title
st.title("Build a RAG System with ChatGPT")

# Directorio que contiene los archivos PDF
pdf_directory = "/app/data"

# Función para inicializar el modelo y el vector store (solo se ejecuta una vez)
@st.cache_resource
def initialize_model_and_retriever():
    all_docs = []
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):  # Verificar que sea un archivo PDF
            file_path = os.path.join(pdf_directory, filename)
            loader = PDFPlumberLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)
    # Dividir en fragmentos
    text_splitter = SemanticChunker(HuggingFaceEmbeddings())
    documents = text_splitter.split_documents(all_docs)
    embedder = HuggingFaceEmbeddings()
    vector = FAISS.from_documents(documents, embedder)
    retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    model_name = "gpt-4o"
    llm = ChatOpenAI(model=model_name, temperature=0)
    return retriever, llm

retriever, llm = initialize_model_and_retriever()

# Define the prompt
prompt = """
0. Habla en español.
1. Usa el context para responder la pregunta al final.
2. Si no sabes la respuesta contesta que no sabes.\n
3. Si la pregunta no tiene sentido, contesta que no tiene sentido.
Context: {context}
Question: {question}
Helpful Answer:"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt)

llm_chain = LLMChain(
    llm=llm,
    prompt=QA_CHAIN_PROMPT,
    callbacks=None,
    verbose=True)

document_prompt = PromptTemplate(
    input_variables=["page_content", "source"],
    template="Context:\ncontent:{page_content}\nsource:{source}",
)

combine_documents_chain = StuffDocumentsChain(
    llm_chain=llm_chain,
    document_variable_name="context",
    document_prompt=document_prompt,
    callbacks=None)

qa = RetrievalQA(
    combine_documents_chain=combine_documents_chain,
    verbose=True,
    retriever=retriever,
    return_source_documents=True)

# User input
user_input = st.text_input("Ask a question related to the PDF :")

# Process user input
if user_input:
    with st.spinner("Processing..."):
        response = qa(user_input)["result"]
        st.write("Response:")
        st.write(response)
