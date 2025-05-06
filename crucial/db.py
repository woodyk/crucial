# File: db.py
# Description: SQLite data model and helpers for Crucial canvas platform
# Author: Ms. White
# Created: 2025-05-06

import sqlite3
from pathlib import Path

from crucial.config import CONFIG
DB_PATH = Path(CONFIG["DATABASE"]["path"])

def init_db():
    """
    Initialize Crucial database with required tables.
    """
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS canvases (
            id TEXT PRIMARY KEY,
            name TEXT,
            width INTEGER,
            height INTEGER,
            background TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canvas_id TEXT,
            action TEXT,
            params TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(canvas_id) REFERENCES canvases(id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            label TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()

def get_db_connection():
    """
    Return a new SQLite connection to the Crucial DB.
    """
    return sqlite3.connect(DB_PATH)
