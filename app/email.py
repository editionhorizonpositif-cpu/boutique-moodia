# app/email.py
import socket
import os
import logging
import aiosmtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")


# TEST TEMPORAIRE
try:
    socket.create_connection((SMTP_HOST, SMTP_PORT), timeout=10)
    logger.info("SMTP accessible")
except Exception as e:
    logger.error(f"SMTP bloqué : {e}")

async def send_download_email(to_email: str, download_url: str, product_title: str):
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP non configuré, email non envoyé.")
        return

    if not to_email:
        logger.warning("Adresse destinataire vide, email non envoyé.")
        return

    message = MIMEText(
        f"Merci pour votre achat !\n\n"
        f"Voici votre lien de téléchargement pour '{product_title}' (valable 10 minutes) :\n"
        f"{download_url}"
    )
    message["From"] = SMTP_FROM or SMTP_USERNAME
    message["To"] = to_email
    message["Subject"] = f"Votre ebook : {product_title}"

    # Choisir la méthode de chiffrement selon le port
    if SMTP_PORT == 465:
        # SSL direct
        tls = True
        start_tls = False
    else:
        # STARTTLS sur port 587
        tls = False
        start_tls = True

    try:
        logger.info(f"Tentative d'envoi à {to_email} via {SMTP_HOST}:{SMTP_PORT} (TLS={tls}, STARTTLS={start_tls})")
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            use_tls=tls,
            start_tls=start_tls,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            timeout=30                   # augmenter le timeout
        )
        logger.info(f"Email envoyé à {to_email}")
    except Exception as e:
        logger.error(f"Erreur envoi email SMTP: {e}")
