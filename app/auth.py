# Raymond Liu 101264487
# Afaq Virk 101338854
# Database setup + creation

import os
from typing import Optional

import psycopg2
from psycopg2 import sql

try:
    from dotenv import load_dotenv, find_dotenv
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path)
except Exception:
    pass


def ensure_database_exists() -> None:
    """Create the target database if it does not already exist using PG* env vars."""
    target_db = os.getenv("PGDATABASE")
    if not target_db:
        # Nothing to do if PG* variables are not being used
        return

    conn_kwargs = dict(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
    )

    # If it already exists, return
    try:
        psycopg2.connect(dbname=target_db, **conn_kwargs).close()
        return
    except psycopg2.OperationalError:
        pass

    # Create DB by connecting to default 'postgres'
    con = psycopg2.connect(dbname="postgres", **conn_kwargs)
    con.autocommit = True
    try:
        with con.cursor() as cur:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
    finally:
        con.close()


def build_database_url() -> Optional[str]:
    """Return SQLAlchemy DATABASE_URL from env; prefer DATABASE_URL, else compose from PG* variables."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    required = ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    if any(not os.getenv(k) for k in required):
        return None

    # Compose SQLAlchemy URL
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT")
    db = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    pwd = os.getenv("PGPASSWORD")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"


