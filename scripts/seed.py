"""Crée les données initiales : 1 200 produits.

Idempotent : ne fait rien si la table products contient déjà des produits.
"""
import os

import psycopg

NB_PRODUITS = 1200


def main() -> None:
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        (existing,) = conn.execute("SELECT count(*) FROM products").fetchone()
        if existing > 0:
            print(f"{existing} produits déjà présents, rien à faire.")
            return

        produits = [
            (f"Produit {i:04d}", round(1 + (i * 37 % 5000) / 100, 2))
            for i in range(1, NB_PRODUITS + 1)
        ]
        with conn.cursor() as cur:
            cur.executemany("INSERT INTO products (name, price) VALUES (%s, %s)", produits)
        print(f"{NB_PRODUITS} produits créés.")


if __name__ == "__main__":
    main()
