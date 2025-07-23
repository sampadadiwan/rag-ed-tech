import streamlit as st
from loader import load_pdf_from_drive
from langgraph_flow import run_qa
from embedder import embed_and_store

import asyncio
import sys
import os

# Fix for Streamlit's threading model on Windows + Gemini async issue
if sys.platform.startswith('win'):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

st.set_page_config(page_title="Learn from Your Book", layout="wide")
st.title("📘 AI Tutor - Learn from Your School Book")

file_id = st.text_input("Enter Google Drive File ID:")

if st.button("Load Document"):
    persist_dir = f"./chroma_store/{file_id}"

    if not os.path.exists(persist_dir):
        raw_text = load_pdf_from_drive(file_id)
        if raw_text:
            st.subheader("Preview of Extracted Text:")
            st.text(raw_text[:1000])  # shows first 1000 characters
            st.success("✅ Document loaded successfully!")
            embed_and_store(raw_text, file_id)
            st.success("📦 Document embedded and stored in vector DB!")
        else:
            st.error("❌ Failed to load PDF.")
    else:
        st.info("ℹ️ Document already embedded. Skipping re-processing.")

query = st.text_input("Ask a question from the book:")

if query:
    st.markdown(f"**You asked:** {query}")

if query and file_id:
    response = run_qa(query, file_id)
    st.markdown("### Answer:")
    st.write(response)
