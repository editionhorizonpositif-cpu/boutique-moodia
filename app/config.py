# app/config.py
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")
MOODIA_JWT_SECRET = os.getenv("MOODIA_JWT_SECRET")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
GOOGLE_DRIVE_CREDENTIALS = os.getenv("GOOGLE_DRIVE_CREDENTIALS")  # ancienne variable (chemin)

# Nouvelle variable : chaîne base64 des credentials Google
_creds_b64 = os.getenv("GOOGLE_DRIVE_CREDENTIALS_BASE64")
if _creds_b64:
    GOOGLE_DRIVE_CREDENTIALS_DICT = json.loads(base64.b64decode(_creds_b64))
else:
    GOOGLE_DRIVE_CREDENTIALS_DICT = None