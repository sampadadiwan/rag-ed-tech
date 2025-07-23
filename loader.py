import io
import os
import PyPDF2
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

CACHE_DIR = "./pdf_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def load_pdf_from_drive(file_id):
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    # ✅ Load credentials from Streamlit secrets
    service_account_info = st.secrets["gdrive"]
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=creds)

    # Check cache
    cached_path = os.path.join(CACHE_DIR, f"{file_id}.pdf")
    if os.path.exists(cached_path):
        with open(cached_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "".join(page.extract_text() or "" for page in reader.pages)

    # Download if not cached
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(cached_path, "wb") as out_file:
        out_file.write(fh.getbuffer())

    fh.seek(0)
    reader = PyPDF2.PdfReader(fh)
    return "".join(page.extract_text() or "" for page in reader.pages)
