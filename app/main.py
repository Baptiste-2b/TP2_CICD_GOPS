import os

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.db import get_conn

# Injectés au build de l'image (voir Dockerfile) : permet de savoir
# en 10 secondes quelle version tourne en production (R4).
APP_VERSION = os.getenv("APP_VERSION", "dev")
GIT_COMMIT = os.getenv("GIT_COMMIT", "unknown")

app = FastAPI(title="API Producteurs", version=APP_VERSION)


class OrderIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class StockIn(BaseModel):
    stock: int = Field(ge=0)


@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION, "commit": GIT_COMMIT}


@app.get("/products")
def list_products(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, name, price, stock FROM products ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset),
        ).fetchall()


@app.put("/products/{product_id}/stock")
def declare_stock(product_id: int, body: StockIn):
    """Le producteur déclare le stock disponible pour un de ses produits."""
    with get_conn() as conn:
        product = conn.execute(
            "UPDATE products SET stock = %s WHERE id = %s "
            "RETURNING id, name, price, stock",
            (body.stock, product_id),
        ).fetchone()
    if product is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return product


@app.post("/orders", status_code=201)
def create_order(order: OrderIn):
    with get_conn() as conn:
        product = conn.execute(
            "SELECT id FROM products WHERE id = %s", (order.product_id,)
        ).fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Produit introuvable")

        return conn.execute(
            "INSERT INTO orders (product_id, quantity) VALUES (%s, %s) "
            "RETURNING id, product_id, quantity, created_at",
            (order.product_id, order.quantity),
        ).fetchone()
