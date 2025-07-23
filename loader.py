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
    if os.path.exi
