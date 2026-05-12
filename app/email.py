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

        logger.info(f"Tentative envoi vers {to_email}")

        response = resend.Emails.send({
            "from": "Moodia <support@moodia.xyz>",
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

        logger.info(f"RESEND RESPONSE: {response}")

    except Exception as e:
        logger.exception(f"Erreur Resend : {e}")
