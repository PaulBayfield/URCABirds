import sqlite3

from src.worker.config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            species TEXT NOT NULL,
            confidence REAL NOT NULL,
            synced INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def cache_detection(timestamp: str, species: str, confidence: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO detections (timestamp, species, confidence, synced) VALUES (?, ?, ?, 0)",
        (timestamp, species, confidence),
    )
    conn.commit()
    conn.close()


def get_unsynced_records():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, timestamp, species, confidence FROM detections WHERE synced = 0"
    )
    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]


def mark_synced(record_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE detections SET synced = 1 WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
