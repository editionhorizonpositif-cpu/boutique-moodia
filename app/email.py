# app/email.py
import asyncio
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Content
from .config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME

logger = logging.getLogger(__name__)

async def send_download_email(to_email: str, download_url: str, product_title: str):
    """Envoie un email de téléchargement via SendGrid (asynchrone)."""
    if not SENDGRID_API_KEY or not SENDGRID_FROM_EMAIL:
        logger.warning("SendGrid non configuré. Email non envoyé.")
        return

    message = Mail(
        from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
        to_emails=to_email,
        subject=f"Votre ebook : {product_title}",
        html_content=Content(
            "text/html",
            f"""
            <p>Merci pour votre achat !</p>
            <p>Voici votre lien de téléchargement pour <strong>{product_title}</strong> (valable 10 minutes) :</p>
            <p><a href="{download_url}">{download_url}</a></p>
            <p>Si vous avez des questions, contactez-nous.</p>
            <p>L'équipe Moodia</p>
            """
        )
    )

    # Exécution synchrone dans un thread pour ne pas bloquer l'event loop
    await asyncio.to_thread(_send_sync, message)

def _send_sync(message: Mail):
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email envoyé à {message.to_emails}, statut: {response.status_code}")
    except Exception as e:
        logger.error(f"Erreur envoi email SendGrid: {e}")
