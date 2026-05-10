# app/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .cart import get_cart
from .models import Cart, Order, OrderItem
from .paypal_client import create_paypal_order

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/checkout")
async def checkout(
    cart: Cart = Depends(get_cart),
    db: AsyncSession = Depends(get_db)
):
    if not cart.items:
        raise HTTPException(400, "Panier vide")
    total = sum(item.product.price * item.quantity for item in cart.items)
    order = Order(total=total, status="PENDING")
    db.add(order)
    await db.flush()
    for item in cart.items:
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        ))
    paypal_order = await create_paypal_order(total)
    order.paypal_order_id = paypal_order.id
    await db.commit()
    approval_url = next(link.href for link in paypal_order.links if link.rel == "approve")
    return {"approval_url": approval_url}