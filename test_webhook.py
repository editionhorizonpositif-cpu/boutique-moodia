# test_webhook.py
import asyncio
from app.database import async_session
from app.models import Product, Order, OrderItem
from app.paypal_client import create_paypal_order

async def main():
    async with async_session() as db:
        product = await db.get(Product, 1)
        if not product:
            print("❌ Produit 1 introuvable. Insérez-le d'abord dans la base.")
            return

        order = Order(total=product.price, status='PENDING')
        db.add(order)
        await db.flush()

        db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=1, price=product.price))

        paypal_order = await create_paypal_order(product.price)
        order.paypal_order_id = paypal_order.id
        await db.commit()

        approval_url = next(link.href for link in paypal_order.links if link.rel == 'approve')
        print("\n✅ URL de paiement :")
        print(approval_url)
        print("\n➡️ Ouvrez cette URL dans votre navigateur et payez avec un compte sandbox.")
        print("ℹ️ Le webhook sera automatiquement envoyé à votre serveur Render.")

asyncio.run(main())