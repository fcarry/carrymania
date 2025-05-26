# filepath: /Users/carry/chatbotdoc/chatbotdoc.py
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA

import os

os.environ["OPENAI_API_KEY"] = "APY_KEY_HERE"  # Replace with your actual OpenAI API key

# Inicializar FastAPI
app = FastAPI()

# Directorio que contiene los archivos PDF
pdf_directory = "/app/data"

# Modelo de entrada para las solicitudes
class QuestionRequest(BaseModel):
    question: str

# Inicializar el modelo y el retriever (solo una vez)
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

# Endpoint para procesar preguntas
@app.post("/ask")
def ask_question(request: QuestionRequest):
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
        verbose=True
    )

    document_prompt = PromptTemplate(
        input_variables=["page_content", "source"],
        template="Context:\ncontent:{page_content}\nsource:{source}",
    )

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
        document_prompt=document_prompt,
        callbacks=None
    )

    qa = RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        verbose=True,
        retriever=retriever,
        return_source_documents=True
    )

    # Procesar la pregunta
    response = qa(request.question)["result"]
    return {"response": response}