# db/connect.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Establish a PostgreSQL connection using DATABASE_URL."""
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL not set in .env")
    return psycopg2.connect(dsn)
