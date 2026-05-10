# app/email.py
import aiosmtplib
from email.mime.text import MIMEText

async def send_download_email(to_email: str, download_url: str, product_title: str):
    message = MIMEText(
        f"Merci pour votre achat !\n\n"
        f"Voici votre lien de téléchargement pour '{product_title}' (valable 10 minutes) :\n"
        f"{download_url}"
    )
    message["From"] = "votre_email@gmail.com"   # À CHANGER
    message["To"] = to_email
    message["Subject"] = "Votre ebook"
    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="votre_email@gmail.com",       # À CHANGER
        password="votre_mot_de_passe_app"       # À CHANGER
    )