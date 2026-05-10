# app/main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine, async_session
from .models import Base
from .downloads import router as downloads_router
from .orders import router as orders_router
from .webhooks import router as webhooks_router
from .front import router as front_router          # <-- NOUVEAU

app = FastAPI(title="Boutique Moodia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(downloads_router)
app.include_router(orders_router)
app.include_router(webhooks_router)
app.include_router(front_router)                  # <-- NOUVEAU

async def keepalive():
    while True:
        await asyncio.sleep(240)
        try:
            async with async_session() as db:
                await db.execute(text("SELECT 1"))
        except Exception as e:
            print(f"Keepalive query failed: {e}")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(keepalive())

@app.get("/")
async def root():
    return {"message": "Boutique Moodia"}