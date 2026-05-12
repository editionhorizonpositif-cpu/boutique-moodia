import os
import io
import json
import base64
import asyncio
import logging

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly"
]


def get_drive_service():

    encoded_credentials = os.getenv(
        "GOOGLE_DRIVE_CREDENTIALS_BASE64"
    )

    if not encoded_credentials:
        raise Exception(
            "GOOGLE_DRIVE_CREDENTIALS_BASE64 introuvable"
        )

    logger.info(
        "Credentials Google Drive détectés"
    )

    credentials_json = base64.b64decode(
        encoded_credentials
    ).decode(
        "utf-8"
    )

    credentials_dict = json.loads(
        credentials_json
    )

    credentials = (
        service_account.Credentials
        .from_service_account_info(
            credentials_dict,
            scopes=SCOPES
        )
    )

    return build(
        "drive",
        "v3",
        credentials=credentials
    )


def _download_file_sync(
    file_id: str
):

    logger.info(
        f"Téléchargement Google Drive: {file_id}"
    )

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

        status, done = (
            downloader.next_chunk()
        )

        if status:

            logger.info(
                f"Progression: "
                f"{int(status.progress()*100)}%"
            )

    file_buffer.seek(0)

    logger.info(
        "Téléchargement terminé"
    )

    return file_buffer


async def download_file(
    file_id: str
):

    return await asyncio.to_thread(
        _download_file_sync,
        file_id
    )
