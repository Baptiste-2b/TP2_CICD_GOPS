import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Les tests qui touchent la base nécessitent DATABASE_URL
# (fourni par la CI avec un PostgreSQL éphémère, ou par docker compose en local).
needs_db = pytest.mark.skipif(
    "DATABASE_URL" not in os.environ, reason="DATABASE_URL non défini"
)


def test_health_retourne_ok_et_version():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "commit" in body


def test_commande_quantite_invalide_refusee():
    response = client.post("/orders", json={"product_id": 1, "quantity": 0})
    assert response.status_code == 422


@needs_db
def test_liste_des_produits():
    response = client.get("/products", params={"limit": 5})
    assert response.status_code == 200
    produits = response.json()
    assert 0 < len(produits) <= 5
    assert {"id", "name", "price", "stock"} <= produits[0].keys()


@needs_db
def test_creation_commande():
    product_id = client.get("/products", params={"limit": 1}).json()[0]["id"]
    response = client.post("/orders", json={"product_id": product_id, "quantity": 2})
    assert response.status_code == 201
    assert response.json()["quantity"] == 2


@needs_db
def test_commande_produit_inexistant():
    response = client.post("/orders", json={"product_id": 999999, "quantity": 1})
    assert response.status_code == 404
