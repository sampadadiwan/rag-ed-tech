import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import PyPDF2

def load_pdf_from_drive(file_id):
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)
    reader = PyPDF2.PdfReader(fh)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
