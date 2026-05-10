# test_drive.py
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Chemin vers votre fichier de clés JSON (à adapter si nécessaire)
SERVICE_ACCOUNT_FILE = "app/google_credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Authentification via le compte de service
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("drive", "v3", credentials=credentials)

# ⚠️ Remplacez par votre propre File ID (la partie après /d/ et avant /view)
FILE_ID = "10BuJwcs5ggl8yfWEEWOQdF0ksh8socQp"  # <-- MODIFIEZ ICI

# Téléchargement du fichier en mémoire
request = service.files().get_media(fileId=FILE_ID)
file_buffer = io.BytesIO()
downloader = MediaIoBaseDownload(file_buffer, request)
done = False
while not done:
    status, done = downloader.next_chunk()
    print(f"Progression : {int(status.progress() * 100)}%")

file_buffer.seek(0)

# Sauvegarde locale pour vérifier que le fichier est complet
with open("test_output.pdf", "wb") as f:
    f.write(file_buffer.read())

print("✅ Téléchargement réussi, fichier sauvegardé sous 'test_output.pdf'")