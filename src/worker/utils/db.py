import sqlite3

from src.worker.config import DB_PATH


class Database:
    """
    Database class for handling SQLite database operations.
    """

    def __init__(self) -> None:
        """
        Initialises the Database class with the default values.
        """
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def init(self) -> None:
        """
        Creates the detections table if it doesn't exist.
        """
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    species TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            """
        )

        self.conn.commit()

    def cache_detection(self, timestamp: str, species: str, confidence: float) -> None:
        """
        Caches a detection in the database.

        :param timestamp: The timestamp of the detection.
        :type timestamp: str
        :param species: The species of the detection.
        :type species: str
        :param confidence: The confidence of the detection.
        :type confidence: float
        """
        self.cursor.execute(
            """
                INSERT INTO detections (timestamp, species, confidence, synced)
                VALUES (?, ?, ?, 0)
            """,
            (timestamp, species, confidence),
        )

        self.conn.commit()

    def get_unsynced_records(self) -> list: 
        """
        Gets all unsynced records from the database.

        :return: A list of unsynced records.
        :rtype: list
        """
        self.cursor.execute(
            """
                SELECT id, timestamp, species, confidence 
                FROM detections WHERE synced = 0
            """
        )
        records = self.cursor.fetchall()
        return [dict(row) for row in records]

    def mark_synced(self, record_id: int) -> None:
        """
        Marks a record as synced in the database.

        :param record_id: The ID of the record to mark as synced.
        :type record_id: int
        """
        self.cursor.execute(
            """
                UPDATE detections SET synced = 1 WHERE id = ?
            """,
            (record_id,),
        )
        self.conn.commit()

    def close(self) -> None: 
        """
        Closes the database connection.
        """
        self.conn.close()
