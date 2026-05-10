# app/cart.py
from fastapi import Request, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .database import get_db
from .models import Cart, CartItem
import uuid

COOKIE_NAME = "cart_session"

async def get_cart(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    session_id = request.cookies.get(COOKIE_NAME)
    cart = None
    if session_id:
        result = await db.execute(
            select(Cart).where(Cart.session_id == session_id).options(selectinload(Cart.items))
        )
        cart = result.scalars().first()
    if not cart:
        session_id = str(uuid.uuid4())
        cart = Cart(session_id=session_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        response.set_cookie(
            COOKIE_NAME,
            session_id,
            httponly=True,
            secure=False,   # True en production avec HTTPS
            samesite="lax",
            max_age=3600*24*30
        )
    return cart