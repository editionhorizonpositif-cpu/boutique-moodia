# app/webhooks.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import Order, WebhookEvent, Product
from .paypal_client import capture_paypal_order
from .downloads import generate_download_token
from .email import send_download_email
import json

router = APIRouter()

@router.post("/webhooks/paypal")
async def paypal_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    # Vérification simplifiée pour le sandbox (à renforcer en prod avec signature)
    body = await request.json()
    event_type = body.get("event_type")
    event_id = body.get("id")

    # Idempotence
    existing = await db.get(WebhookEvent, event_id)
    if existing:
        return {"message": "Événement déjà traité"}

    db.add(WebhookEvent(event_id=event_id))
    await db.flush()

    if event_type == "CHECKOUT.ORDER.APPROVED":
        order_id = body['resource']['id']
        result = await db.execute(select(Order).where(Order.paypal_order_id == order_id))
        order = result.scalars().first()
        if order and order.status == "PENDING":
            await capture_paypal_order(order_id)
            order.status = "COMPLETED"
            # Récupère l'email du payeur si disponible (sinon valeur par défaut)
            payer_email = body.get('resource', {}).get('payer', {}).get('email_address', 'client@example.com')
            order.customer_email = payer_email
            await db.commit()

            # Envoi du lien de téléchargement pour chaque produit de la commande
            for item in order.items:
                product = await db.get(Product, item.product_id)
                token = generate_download_token(product.id)
                download_url = f"http://127.0.0.1:8000/download/ebook?token={token}"
                await send_download_email(payer_email, download_url, product.title)

    return {"message": "OK"}