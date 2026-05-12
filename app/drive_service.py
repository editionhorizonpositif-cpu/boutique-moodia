import asyncio
import io
import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .config import GOOGLE_DRIVE_CREDENTIALS

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly"
]


def get_drive_service():

    if not GOOGLE_DRIVE_CREDENTIALS:
        raise Exception(
            "GOOGLE_DRIVE_CREDENTIALS non configuré sur le serveur"
        )

    logger.info(
        f"Google credentials path = {GOOGLE_DRIVE_CREDENTIALS}"
    )

    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_DRIVE_CREDENTIALS,
        scopes=SCOPES
    )

    return build(
        "drive",
        "v3",
        credentials=credentials
    )


def _download_file_sync(file_id: str) -> io.BytesIO:

    logger.info(f"Téléchargement Google Drive : {file_id}")

    service = get_drive_service()

    request = service.files().get_media(
        fileId=file_id
    )

    file_buffer = io.BytesIO()

    downloader = MediaIoBaseDownload(
        file_buffer,
        request
    )

    done = False

    while not done:
        status, done = downloader.next_chunk()

        if status:
            logger.info(
                f"Progression: {int(status.progress() * 100)}%"
            )

    file_buffer.seek(0)

    logger.info("Téléchargement terminé")

    return file_buffer


async def download_file(file_id: str) -> io.BytesIO:
    return await asyncio.to_thread(
        _download_file_sync,
        file_id
    )
