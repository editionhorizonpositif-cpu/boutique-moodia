# check_product.py
import asyncio
from app.database import async_session
from app.models import Product

async def main():
    async with async_session() as db:
        product = await db.get(Product, 1)
        if product:
            print("ID:", product.id)
            print("Titre:", product.title)
            print("content_file_id:", product.content_file_id)
            print("content_name:", product.content_name)
        else:
            print("Produit 1 introuvable")
            return
        if not product.content_file_id:
            product.content_file_id = "10BuJwcs5ggl8yfWEEWOQdF0ksh8socQp"
            product.content_name = "ebook_test.pdf"
            await db.commit()
            print("✅ Produit mis à jour avec le bon File ID.")

asyncio.run(main())