from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.llms import Ollama
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from sqlalchemy import create_engine
import json

# 📌 1️⃣ Inicializar FastAPI
app = FastAPI()

# 📌 2️⃣ Conectar a la base de datos MySQL
DB_URL = "mysql+pymysql://usuario:contraseña@localhost/supermercado"
engine = create_engine(DB_URL)

# 📌 3️⃣ Obtener el esquema de la base de datos dinámicamente
def obtener_esquema_mysql():
    try:
        with engine.connect() as connection:
            # Obtener nombres de las tablas
            result = connection.execute("SHOW TABLES").fetchall()
            tablas = [row[0] for row in result]

            esquema = {}

            for tabla in tablas:
                # Obtener columnas de cada tabla
                result = connection.execute(f"DESCRIBE {tabla}").fetchall()
                columnas = [{ "nombre": row[0], "tipo": row[1] } for row in result]
                esquema[tabla] = columnas

        return json.dumps(esquema, indent=2)
    except Exception as e:
        return f"Error al obtener el esquema: {str(e)}"

# 📌 4️⃣ Guardar el esquema en la base vectorial
schema_info = obtener_esquema_mysql()
documents = [schema_info]
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_texts(documents, embeddings)

# 📌 5️⃣ Configurar el LLM con RAG
retriever = vector_store.as_retriever()
llm = Ollama(model="deepseek-r1")
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

# 📌 6️⃣ Modelo de datos para FastAPI
class QueryRequest(BaseModel):
    question: str

# 📌 7️⃣ Función para procesar la pregunta y generar respuesta
def query_llm_with_rag(prompt):
    try:
        # Generar la consulta SQL basada en el esquema dinámico
        query_sql = qa_chain.run(f"Usando el esquema de la BD: {schema_info}, genera una consulta SQL para: {prompt}")

        # Ejecutar la consulta y obtener los resultados
        result = engine.execute(query_sql).fetchall()
        json_result = json.dumps([dict(row) for row in result])

        # Usar el LLM para interpretar los resultados en lenguaje natural
        human_response = llm.invoke(f"Usando los datos obtenidos: {json_result}, responde de forma natural a la pregunta: {prompt}")

        return human_response
    except Exception as e:
        return f"Error al procesar la consulta: {str(e)}"

# 📌 8️⃣ Endpoint para recibir la consulta del usuario
@app.post("/query")
async def handle_query(request: QueryRequest):
    respuesta = query_llm_with_rag(request.question)
    if not respuesta:
        raise HTTPException(status_code=400, detail="No se pudo generar la respuesta.")
    return {"question": request.question, "answer": respuesta}