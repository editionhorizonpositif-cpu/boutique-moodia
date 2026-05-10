# app/front.py
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import Product, Cart, CartItem, Order, OrderItem
from .cart import get_cart
from .paypal_client import create_paypal_order
import os

router = APIRouter()

# --- Initialisation manuelle de Jinja2 (évite le bug LruCache de Starlette sur Python 3.14) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jinja_env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "app/templates")))

def render_template(name: str, context: dict) -> HTMLResponse:
    template = jinja_env.get_template(name)
    return HTMLResponse(template.render(context))

# ---------- Page boutique ----------
@router.get("/shop")
async def shop(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return render_template("shop.html", {"request": request, "products": products})

# ---------- Ajouter au panier (version robuste sans lazy loading) ----------
@router.get("/cart/add/{product_id}")
async def add_to_cart(product_id: int, cart: Cart = Depends(get_cart), db: AsyncSession = Depends(get_db)):
    # Vérifier que le produit existe
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Produit introuvable")

    # Chercher si déjà dans le panier (requête explicite)
    stmt = select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
    result = await db.execute(stmt)
    existing = result.scalars().first()

    if existing:
        existing.quantity += 1
        await db.commit()
    else:
        new_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
        db.add(new_item)
        await db.commit()

    return RedirectResponse("/cart", status_code=303)

# ---------- Supprimer du panier (version robuste) ----------
@router.get("/cart/remove/{product_id}")
async def remove_from_cart(product_id: int, cart: Cart = Depends(get_cart), db: AsyncSession = Depends(get_db)):
    stmt = select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
    return RedirectResponse("/cart", status_code=303)

# ---------- Voir le panier (avec selectinload) ----------
@router.get("/cart")
async def view_cart(request: Request, cart: Cart = Depends(get_cart), db: AsyncSession = Depends(get_db)):
    # Charger les items AVEC les produits en une seule requête
    stmt = select(CartItem).where(CartItem.cart_id == cart.id).options(selectinload(CartItem.product))
    result = await db.execute(stmt)
    items = result.scalars().all()

    cart_items = []
    total = 0
    for item in items:
        if item.product:
            cart_items.append({"product": item.product, "quantity": item.quantity})
            total += item.product.price * item.quantity

    return render_template("cart.html", {
        "request": request,
        "cart_items": cart_items,
        "total": total
    })

# ---------- Acheter directement un produit ----------
@router.get("/buy/{product_id}")
async def buy_now(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(404)
    order = Order(total=product.price, status="PENDING")
    db.add(order)
    await db.flush()
    db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=1, price=product.price))
    paypal_order = await create_paypal_order(product.price)
    order.paypal_order_id = paypal_order.id
    await db.commit()
    approval_url = next(link.href for link in paypal_order.links if link.rel == "approve")
    return RedirectResponse(approval_url, status_code=303)

# ---------- Checkout du panier ----------
@router.get("/checkout")
async def checkout(cart: Cart = Depends(get_cart), db: AsyncSession = Depends(get_db)):
    if not cart.items:
        raise HTTPException(400, "Panier vide")
    total = 0
    items_list = []
    for item in cart.items:
        product = await db.get(Product, item.product_id)
        if product:
            items_list.append((product, item.quantity))
            total += product.price * item.quantity
    if total == 0:
        raise HTTPException(400, "Panier vide")
    order = Order(total=total, status="PENDING")
    db.add(order)
    await db.flush()
    for product, qty in items_list:
        db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=product.price))
    paypal_order = await create_paypal_order(total)
    order.paypal_order_id = paypal_order.id
    await db.commit()
    for item in cart.items:
        await db.delete(item)
    await db.commit()
    approval_url = next(link.href for link in paypal_order.links if link.rel == "approve")
    return RedirectResponse(approval_url, status_code=303)

# ---------- TEST JSON (à supprimer après) ----------
@router.get("/cart-json")
async def view_cart_json(cart: Cart = Depends(get_cart), db: AsyncSession = Depends(get_db)):
    stmt = select(CartItem).where(CartItem.cart_id == cart.id).options(selectinload(CartItem.product))
    result = await db.execute(stmt)
    items = result.scalars().all()
    return {
        "session_id": cart.session_id,
        "cart_id": cart.id,
        "items": [{"product": item.product.title, "quantity": item.quantity} for item in items if item.product]
    }

# ---------- Page de succès ----------
@router.get("/payment-success")
async def payment_success(request: Request):
    return render_template("success.html", {"request": request})
