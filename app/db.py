import os

import psycopg
from psycopg.rows import dict_row


def get_conn() -> psycopg.Connection:
    """Ouvre une connexion PostgreSQL à partir de DATABASE_URL (jamais codée en dur)."""
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)
