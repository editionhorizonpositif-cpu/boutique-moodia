# test_checkout.py
import asyncio
from app.database import async_session
from app.models import Product, Order, OrderItem
from app.paypal_client import create_paypal_order

PRODUCT_ID = 1  # L'ID du produit inséré

async def test():
    async with async_session() as db:
        product = await db.get(Product, PRODUCT_ID)
        if not product:
            print(f"Produit {PRODUCT_ID} introuvable.")
            return

        # Création de la commande
        order = Order(total=product.price, status="PENDING")
        db.add(order)
        await db.flush()  # pour avoir l'ID

        db.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price=product.price
        ))

        # Création de la commande PayPal
        paypal_order = await create_paypal_order(product.price)
        order.paypal_order_id = paypal_order.id
        await db.commit()

        # URL d'approbation
        approval_url = next(link.href for link in paypal_order.links if link.rel == "approve")
        print("\n✅ Copiez cette URL pour payer :")
        print(approval_url)
        print("\nID de la commande locale :", order.id)
        print("ID PayPal :", paypal_order.id)

asyncio.run(test())