# app/drive_service.py
import asyncio
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from .config import GOOGLE_DRIVE_CREDENTIALS

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_DRIVE_CREDENTIALS, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=credentials)

def _download_file_sync(file_id: str) -> io.BytesIO:
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    file_buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(file_buffer, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file_buffer.seek(0)
    return file_buffer

async def download_file(file_id: str) -> io.BytesIO:
    return await asyncio.to_thread(_download_file_sync, file_id)