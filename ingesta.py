import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter #Corta todo el PDF en Chunks
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings #Conversor de Texto a Vectores
from langchain_qdrant import QdrantVectorStore

load_dotenv() #Lee el archivo .env que hemos creado

def cargar_biblioteca_local(lista_pdfs):
    # Inicializamos embeddings y el splitter
    embeddings = OpenAIEmbeddings() #Conversor de Texto a Vectores (numeros)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150) #Corta todo el PDF en Chunks
    
    docs_totales = []
    for pdf in lista_pdfs:
        if os.path.exists(pdf):
            print(f"Procesando: {pdf}...")
            loader = PyPDFLoader(pdf) #Cargador de archivos PDFs
            docs_totales.extend(loader.load()) # Extrae el texto de todas las páginas y las añade a la lista 'docs_totales'.
        else:
            print(f"⚠️ Archivo no encontrado: {pdf}")
    
    chunks = splitter.split_documents(docs_totales)
    
    print(f"Guardando {len(chunks)} fragmentos en la base de datos local...")
    
    # Ingesta en la base de datos
    QdrantVectorStore.from_documents( #La integración para guardar vectores en Qdrant.
        chunks,
        embeddings,
        path="./db_harry_potter",
        collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
        force_recreate=True  # Asegura que la colección sea nueva y limpia
    )
    print("¡LOGRADO! Ingesta completada con éxito en './db_harry_potter'.")

if __name__ == "__main__": #para que se ejecute solo cuando ejecutemos directamente este script
    libros = [
        "Harry_Potter_y_la_Piedra_Filosofal-J_K_Rowling.pdf", 
        "HARRY POTTER Y LA CAMARA SECRETA.pdf"
    ]
    cargar_biblioteca_local(libros) # Llama a la función definida arriba pasándole la lista de libros para que empiece a trabajar.