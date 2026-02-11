import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException # Framework para crear la API y el sistema de errores.
from pydantic import BaseModel # Herramienta para definir qué estructura deben tener los datos que recibe la API.
from langchain_openai import ChatOpenAI, OpenAIEmbeddings #El LLM y el Embedding de OpenAI
from qdrant_client import QdrantClient #Para comunicarnos con la bbdd vectorial

load_dotenv()
app = FastAPI(title="Hogwarts Oracle Pro") # Crecion de la aplicación web Swagger

class QueryRequest(BaseModel): # Define una clase para validar que el usuario siempre envíe un texto llamado "query".
    query: str

# Inicialización de modelos
embeddings_model = OpenAIEmbeddings() #Preparamos traductor para traducir "query" en vectores
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0) #Config de la IA para que sea precisa

# Conexión directa
client = QdrantClient(path="./db_harry_potter") #Abrimos la bbdd vectorial
collection_name = os.getenv("QDRANT_COLLECTION_NAME") #sacamos nombre del .env

@app.post("/preguntar") # Creamos la"puerta" tipo POST donde el frontend podrá enviar preguntas.
async def preguntar(request: QueryRequest): # Definimos función asíncrona (async) para no bloquear el servidor mientras la IA piensa.
    try:
        pregunta_vector = embeddings_model.embed_query(request.query) # Convierte la pregunta del usuario en una lista de números (vector).

        search_result = client.query_points( # Pedimos a Qdrant buscar en la bbdd
            collection_name=collection_name, # Decimos en qué coleccion buscar
            query=pregunta_vector, #Le damos el vector de la "query" para buscar por similitud
            limit=4 #máximo de fragmentos más parecidos
        ).points #para traer solo los datos sin metadata

        # Juntamos los 4 fragmentos en un solo parrafo separado por rayas para que la IA los lea.
        contexto = "\n---\n".join([res.payload["page_content"] for res in search_result])
        
        # Creamos una lista con los nombres de los archivos PDF originales donde encontró la información, sin repetir nombres.
        fuentes = list(set([os.path.basename(res.payload["metadata"]["source"]) for res in search_result]))

        # PROMPT DE RESTRICCIÓN TOTAL (GUARDRAILS)
        prompt = f"""Eres un sistema de recuperación de información CERRADO. 
        Tu única fuente de verdad es el CONTEXTO que te proporciono abajo.

        REGLAS CRÍTICAS:
        1. Si la respuesta NO aparece explícitamente en el CONTEXTO, responde exactamente: "Lo siento, pero esa información no está en los libros de la Piedra Filosofal o la Cámara Secreta."
        2. NO uses tus conocimientos externos ni menciones eventos de libros que NO esten incluidos en la base de datos.
        3. No inventes nada.

        CONTEXTO:
        {contexto}
        
        PREGUNTA: {request.query}
        
        RESPUESTA:""" # Este es el texto final que se le envía a la IA con las instrucciones y la información encontrada.

        respuesta = llm.invoke(prompt) # Llamamos a la IA de OpenAI enviándole el prompt y espera la respuesta.

        return { # Devolvemos la respuesta al frontend en formato JSON.
            "respuesta": respuesta.content, #Respuesta generada por la IA
            "fuentes_consultadas": fuentes #Nombres de los libros donde sacó la info
        }
    except Exception as e: #Por si algo falla
        print(f"Error: {e}") #Imprimimos el error en la consola para verlo
        raise HTTPException(status_code=500, detail=str(e)) #Envia un error 500 el user para decirle que salio mal