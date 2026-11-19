"""Applique les migrations SQL de migrations/ dans l'ordre, une seule fois chacune (R3).

Les migrations déjà appliquées sont enregistrées dans la table schema_migrations.
Lancé automatiquement au démarrage du conteneur API et par la CI.
"""
import os
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def main() -> None:
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " version TEXT PRIMARY KEY,"
            " applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
        )
        applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}

        for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if migration.name in applied:
                continue
            print(f"Application de la migration {migration.name}")
            conn.execute(migration.read_text(encoding="utf-8"))
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)", (migration.name,)
            )


if __name__ == "__main__":
    main()
