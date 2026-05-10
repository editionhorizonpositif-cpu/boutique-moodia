# app/downloads.py
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .config import APP_SECRET_KEY
from .database import get_db
from .models import Product
from .drive_service import download_file

router = APIRouter(prefix="/download", tags=["download"])
serializer = URLSafeTimedSerializer(APP_SECRET_KEY)

def generate_download_token(product_id: int, user_identifier: str = ""):
    return serializer.dumps({"product_id": product_id, "user": user_identifier})

@router.get("/ebook")
async def download_ebook(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Vérifier le token
    max_age = 600  # 10 minutes
    try:
        data = serializer.loads(token, max_age=max_age)
    except Exception:
        raise HTTPException(403, "Lien invalide ou expiré")

    product_id = data["product_id"]
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(404, "Produit introuvable")

    file_id = product.content_file_id
    if not file_id:
        raise HTTPException(404, "Fichier non référencé")

    try:
        buffer = await download_file(file_id)
    except Exception as e:
        raise HTTPException(500, f"Erreur lors du téléchargement du fichier: {str(e)}")

    filename = product.content_name or "fichier"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        buffer,
        media_type="application/octet-stream",
        headers=headers
    )