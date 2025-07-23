from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import asyncio
import sys
from vectorstore import get_vectorstore, store_documents
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Fix for Streamlit's threading model on Windows + Gemini async issue
if sys.platform.startswith('win'):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

load_dotenv()

def get_gemini_embedder():
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

def embed_and_store(raw_text: str, file_id: str) -> None:
    """
    Splits the raw_text into chunks, generates embeddings using Gemini,
    and stores them in a Chroma vector DB using file_id as a unique directory.
    """
    persist_dir = f"./chroma_store/{file_id}"

    # 1. Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents([raw_text])

    # 2. Get embeddings
    embedder = get_gemini_embedder()
    
    vectorstore = get_vectorstore(embedder, file_id)

    # Store into vector db
    texts = [doc.page_content for doc in docs]
    print(f"Storing {len(texts)} chunks in Chroma vector DB at {persist_dir}")
    print("0th Chunks:", texts[0])
    store_documents(texts, vectorstore)

    # 3. Store in Chroma vector DB
    #db = Chroma.from_documents(docs, embedding=embedder, persist_directory=persist_dir)
    #db.persist()
