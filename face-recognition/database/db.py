"""
db.py
HemaGrid AI - Local Database Interface

Manages SQLite storage for donor metadata and serialized face landmarks.
"""

import json
import sqlite3
from datetime import datetime, timedelta

class DonorDatabase:
    def __init__(self, db_path="donors.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS donors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    landmarks TEXT NOT NULL
                )
            """)
            conn.commit()

    def enroll_donor(self, name: str, landmarks: list) -> int:
        """
        Inserts a new donor record into the SQLite database.
        
        Args:
            name (str): Full name of the donor.
            landmarks (list): Flat list of 1404 floats representing face landmarks.
            
        Returns:
            int: The primary key ID of the enrolled donor.
        """
        landmarks_json = json.dumps(landmarks)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO donors (name, landmarks) VALUES (?, ?)",
                (name, landmarks_json)
            )
            conn.commit()
            return cursor.lastrowid

    def get_recent_donors(self, days_limit=56) -> list:
        """
        Retrieves donor records registered within the safety lockout window
        (e.g., standard clinical limit is 56 days between whole blood donations).
        
        Args:
            days_limit (int): Lockout window in days.
            
        Returns:
            list: List of dicts representing enrolled donors.
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days_limit)).strftime('%Y-%m-%d %H:%M:%S')
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, enrolled_at, landmarks FROM donors WHERE enrolled_at >= ?",
                (cutoff_date,)
            )
            rows = cursor.fetchall()
            
            donors = []
            for row in rows:
                donors.append({
                    "id": row["id"],
                    "name": row["name"],
                    "enrolled_at": row["enrolled_at"],
                    "landmarks": json.loads(row["landmarks"])
                })
            return donors
            
    def clear_database(self):
        """
        Clears all tables. Primarily used for unit testing.
        """
        with self._get_connection() as conn:
            conn.execute("DELETE FROM donors")
            conn.commit()
