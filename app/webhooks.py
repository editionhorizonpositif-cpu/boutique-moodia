# app/webhooks.py
import json
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .database import get_db
from .models import Order, OrderItem, WebhookEvent, Product
from .paypal_client import capture_paypal_order
from .downloads import generate_download_token
from .email import send_download_email

router = APIRouter()

@router.post("/webhooks/paypal")
async def paypal_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    event_body = json.loads(body.decode())
    event_type = event_body.get("event_type")
    event_id = event_body.get("id")

    # Idempotence : vérifier si l'événement a déjà été traité
    existing = await db.execute(
        select(WebhookEvent).where(WebhookEvent.event_id == event_id)
    )
    if existing.scalars().first():
        return {"message": "Événement déjà traité"}

    # Enregistrer l'événement
    db.add(WebhookEvent(event_id=event_id))
    await db.flush()

    if event_type == "CHECKOUT.ORDER.APPROVED":
        resource = event_body.get("resource", {})
        paypal_order_id = resource.get("id")
        payer_email = resource.get("payer", {}).get("email_address")

        # Charger la commande AVEC les items et produits
        stmt = select(Order).where(Order.paypal_order_id == paypal_order_id).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        result = await db.execute(stmt)
        order = result.scalars().first()

        if order and order.status == "PENDING":
            await capture_paypal_order(paypal_order_id)
            order.status = "COMPLETED"
            order.customer_email = payer_email
            await db.commit()

            for item in order.items:
                product = item.product
                if product and product.content_file_id:
                    token = generate_download_token(product.id)
                    download_url = f"https://api-boutique.moodia.xyz/download/ebook?token={token}"
                    await send_download_email(
                        to_email=payer_email,
                        download_url=download_url,
                        product_title=product.title
                    )

    return {"message": "OK"}
