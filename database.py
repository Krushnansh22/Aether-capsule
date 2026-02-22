import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = 'aether.db'


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS capsules (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    NOT NULL,
                message     TEXT    NOT NULL,
                file_path   TEXT,
                created_at  TEXT    NOT NULL,
                send_date   TEXT    NOT NULL,
                delivered   INTEGER NOT NULL DEFAULT 0,
                delivered_at TEXT
            )
        ''')
        conn.commit()
        logger.info("Database initialized.")
    finally:
        conn.close()


def save_capsule(email: str, message: str, file_path: str | None, send_date: datetime) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            '''INSERT INTO capsules (email, message, file_path, created_at, send_date, delivered)
               VALUES (?, ?, ?, ?, ?, 0)''',
            (email, message, file_path,
             datetime.now().isoformat(),
             send_date.isoformat())
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_due_capsules(as_of: datetime) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            '''SELECT * FROM capsules
               WHERE delivered = 0
                 AND send_date <= ?''',
            (as_of.isoformat(),)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def mark_delivered(capsule_id: int):
    conn = get_connection()
    try:
        conn.execute(
            '''UPDATE capsules
               SET delivered = 1, delivered_at = ?
               WHERE id = ?''',
            (datetime.now().isoformat(), capsule_id)
        )
        conn.commit()
        logger.info(f"Capsule {capsule_id} marked as delivered.")
    finally:
        conn.close()
