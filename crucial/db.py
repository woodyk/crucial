#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: db.py
# Description: SQLite data model and helpers for Crucial canvas platform
# Author: Ms. White
# Created: 2025-05-06
# Modified: 2025-05-09 21:02:47

import time
import sqlite3
from pathlib import Path
from crucial.config import CONFIG, get_logger

logger = get_logger(__name__)

DB_PATH = Path(CONFIG["DATABASE"]["path"])

# Define expected schema
TABLE_DEFINITIONS = {
    "canvases": {
        "id": "TEXT PRIMARY KEY",
        "human_id": "TEXT UNIQUE",
        "name": "TEXT",
        "width": "INTEGER",
        "height": "INTEGER",
        "background": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    },
    "actions": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "canvas_id": "TEXT",
        "action": "TEXT",
        "params": "TEXT",
        "timestamp": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    },
    "api_keys": {
        "key": "TEXT PRIMARY KEY",
        "label": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
}

def init_db():
    """
    Create all Crucial database tables if not already present.
    """
    with sqlite3.connect(DB_PATH) as conn:
        logger.info("Initializing database at %s", DB_PATH)
        _ensure_tables_exist(conn)

def get_db_connection():
    """
    Return a SQLite connection, automatically ensuring DB schema is current.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    logger.debug("Opened DB connection to %s", DB_PATH)
    _ensure_tables_exist(conn)
    return conn

def _ensure_tables_exist(conn):
    """
    Create missing tables and upgrade schema by adding missing columns.
    """
    cursor = conn.cursor()
    existing_tables = _get_existing_tables(cursor)

    for table, columns in TABLE_DEFINITIONS.items():
        if table not in existing_tables:
            # Create full table
            col_defs = ",\n    ".join([f"{name} {ctype}" for name, ctype in columns.items()])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (\n    {col_defs}\n)")
        else:
            # Check for missing columns and patch them
            cursor.execute(f"PRAGMA table_info({table})")
            existing_columns = {row[1] for row in cursor.fetchall()}
            for col_name, col_type in columns.items():
                if col_name not in existing_columns:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")

    conn.commit()
    logger.debug("Ensured DB tables are up to date")

def _get_existing_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row[0] for row in cursor.fetchall()}

def cleanup_expired_canvases():
    ttl = CONFIG["CANVAS"]["ttl_seconds"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM canvases
        WHERE datetime(created_at) < datetime('now', ? || ' seconds')
    """, (-ttl,))
    expired = [row["id"] for row in cur.fetchall()]

    if not expired:
        logger.info("No expired canvases to clean.")
        return

    cur.executemany("DELETE FROM actions WHERE canvas_id = ?", [(cid,) for cid in expired])
    cur.executemany("DELETE FROM canvases WHERE id = ?", [(cid,) for cid in expired])
    conn.commit()

    logger.info("Expired canvas cleanup complete. Removed %d canvases", len(expired))

