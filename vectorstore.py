from langchain.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from typing import List
import os

def get_vectorstore(embedding_model: Embeddings, file_id: str):
    persist_dir = f"./chroma_store/{file_id}"
    os.makedirs(persist_dir, exist_ok=True)
    return Chroma(
        collection_name="school-book",
        embedding_function=embedding_model,
        persist_directory=persist_dir
    )

def store_documents(texts: List[str], vectorstore: Chroma):
    vectorstore.add_texts(texts)
    vectorstore.persist()  # ✅ ensure vectors are saved to disk

def retrieve_documents(query: str, vectorstore: Chroma):
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(query)
    return docs
