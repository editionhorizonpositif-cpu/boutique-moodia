import os
import logging
import resend

logger = logging.getLogger(__name__)

resend.api_key = os.getenv("RESEND_API_KEY")


async def send_download_email(
    to_email: str,
    download_url: str,
    product_title: str
):
    try:

        resend.Emails.send({
            "from": "Moodia <onboarding@resend.dev>",
            "to": [to_email],
            "subject": f"Votre ebook : {product_title}",
            "html": f"""
                <h2>Merci pour votre achat 🎉</h2>

                <p>Votre ebook <b>{product_title}</b> est prêt.</p>

                <p>
                    <a href="{download_url}">
                        Télécharger maintenant
                    </a>
                </p>
            """
        })

        logger.info(f"Email envoyé à {to_email}")

    except Exception as e:
        logger.error(f"Erreur Resend : {e}")
