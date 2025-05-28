# filepath: /Users/carry/chatbotdoc/chatbotdoc.py
from fastapi import FastAPI
from pydantic import BaseModel
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains import RetrievalQA
from sqlalchemy import create_engine
from sqlalchemy import text
import json
import os

os.environ["OPENAI_API_KEY"] = "APY_KEY"

DB_URL = "mysql+pymysql://chatbotuser:password123456@localhost/chatbotdb"
engine = create_engine(DB_URL)

# Inicializar FastAPI
app = FastAPI()

# Modelo de entrada para las solicitudes
class QuestionRequest(BaseModel):
    question: str

def obtener_esquema_mysql():
    try:
        with engine.connect() as connection:
            # Obtener nombres de las tablas
            result = connection.execute(text("SHOW TABLES")).fetchall()
            tablas = [row[0] for row in result]

            esquema = {}

            for tabla in tablas:
                # Obtener columnas de cada tabla
                result = connection.execute(text(f"DESCRIBE {tabla}")).fetchall()
                columnas = [{ "nombre": row[0], "tipo": row[1] } for row in result]
                esquema[tabla] = columnas

        return json.dumps(esquema, indent=2)
    except Exception as e:
        print(f"Error al obtener el esquema: {str(e)}")
        return f"Error al obtener el esquema: {str(e)}"

# 📌 4️⃣ Guardar el esquema en la base vectorial
schema_info = obtener_esquema_mysql()

documents = [json.dumps({
        "page_content": schema_info
    }, indent=2)]

embeddings = OpenAIEmbeddings()
vector = FAISS.from_texts(documents, embeddings)
retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": 3})
model_name = "gpt-4o"
llm = ChatOpenAI(model=model_name, temperature=0)

# Endpoint para procesar preguntas
@app.post("/ask")
def ask_question(request: QuestionRequest):
    promptSQL = """
    1. Usa el context para responder la pregunta al final y considera que el context es el schema de la base de datos.
    2. Si no sabes la respuesta contesta: SELECT 0;\n
    3. Considerando el schema de la base de datos genera una consulta SQL para responder a Question
    4. Comienza tu respuesta con SELECT y finaliza con ;
    5. Es my importante que tu respuesta sea solo una consulta sql SELECT ejecutable, no le agregues mas texto como SQL al inicio ni ninguna otra cosa que no sea solo responder la consulta SQL ejecutable
    Context: {context}
    Question: {question}
    Helpful Answer:"""

    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(promptSQL)

    llm_chainSQL = LLMChain(
        llm=llm,
        prompt=QA_CHAIN_PROMPT,
        callbacks=None,
        verbose=True
    )

    document_prompt = PromptTemplate(
        input_variables=["page_content"],
        template="Context:\ncontent:{page_content}\n",
    )

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chainSQL,
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
    query_sql = qa(request.question)["result"]
    query_sql=query_sql.replace("sql", "").replace("\n", " ").replace("`","").replace("`","")
    print(f"Consulta SQL generada: {query_sql}")
    qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
    con = engine.connect()
    result = con.execute(text(query_sql)).fetchall()
    print(f"Resultado de la consulta  {result}")
    
    human_response = qa_chain.run(f"Previamente buscamos en la base de datos los datos consultados y el resultado es: {result}, ahora considerando este resultado responde de forma natural a la pregunta: {request.question}")

    
    
    return {"response": human_response}