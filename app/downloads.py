from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import APP_SECRET_KEY
from .database import get_db
from .models import Product

router = APIRouter(prefix="/download", tags=["download"])
serializer = URLSafeTimedSerializer(APP_SECRET_KEY)


def generate_download_token(product_id: int, user_identifier: str = ""):
    return serializer.dumps({
        "product_id": product_id,
        "user": user_identifier
    })


@router.get("/ebook")
async def download_ebook(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):

    # 1. Vérifier le token
    try:
        payload = serializer.loads(token, max_age=600)
    except Exception:
        raise HTTPException(403, "Lien invalide ou expiré")

    product_id = payload["product_id"]

    # 2. Récupérer produit
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalars().first()

    if not product:
        raise HTTPException(404, "Produit introuvable")

    # 3. Vérifier fichier Drive
    file_id = product.content_file_id

    if not file_id:
        raise HTTPException(404, "Fichier non référencé")

    # 4. Redirection directe vers Google Drive
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    return RedirectResponse(
        url=download_url,
        status_code=302
    )
