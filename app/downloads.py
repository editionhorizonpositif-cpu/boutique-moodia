import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from fastapi.responses import StreamingResponse

from itsdangerous import URLSafeTimedSerializer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import APP_SECRET_KEY
from .database import get_db
from .models import Product
from .drive_service import download_file


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/download",
    tags=["download"]
)

serializer = URLSafeTimedSerializer(
    APP_SECRET_KEY
)


def generate_download_token(
    product_id: int,
    user_identifier: str = ""
):
    return serializer.dumps({
        "product_id": product_id,
        "user": user_identifier
    })


@router.get("/ebook")
async def download_ebook(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):

    try:
        payload = serializer.loads(
            token,
            max_age=600
        )

    except Exception:
        raise HTTPException(
            403,
            "Lien invalide ou expiré"
        )

    product_id = payload["product_id"]

    logger.info(
        f"Téléchargement demandé pour produit {product_id}"
    )

    result = await db.execute(
        select(Product).where(
            Product.id == product_id
        )
    )

    product = result.scalars().first()

    if not product:
        raise HTTPException(
            404,
            "Produit introuvable"
        )

    file_id = product.content_file_id

    logger.info(
        f"Google file_id = {file_id}"
    )

    if not file_id:
        raise HTTPException(
            404,
            "Fichier non référencé"
        )

    try:

        buffer = await download_file(
            file_id
        )

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            500,
            f"Erreur téléchargement : {str(e)}"
        )

    filename = (
        product.content_name
        or
        "ebook.pdf"
    )

    headers = {
        "Content-Disposition":
        f'attachment; filename="{filename}"'
    }

    return StreamingResponse(
        buffer,
        media_type="application/octet-stream",
        headers=headers
    )
