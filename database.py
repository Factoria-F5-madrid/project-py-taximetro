import sqlite3
from contextlib import contextmanager
from datetime import datetime


class TripDatabase:
    """Manages taxi trip history using an SQLite database."""

    def __init__(self, db_path="taximeter.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _init_db(self):
        """Create the trips table if it does not already exist."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start TEXT NOT NULL,
                    end TEXT NOT NULL,
                    total_eur REAL NOT NULL
                )
                """
            )

    def save(self, trip):
        """Save a trip to the database."""
        if isinstance(trip, dict):
            start = trip["start"]
            end = trip["end"]
            total = trip["total_eur"]
        else:
            start = trip.start_time
            end = datetime.now().isoformat(timespec="seconds")
            total = trip.total

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO trips (start, end, total_eur) VALUES (?, ?, ?)",
                (start, end, round(total, 2)),
            )

    @staticmethod
    def total_of(trips):
        """Return the sum of the totals of a list of saved trips."""
        return sum(t["total_eur"] for t in trips)

    def load(self):
        """Return all saved trips as a list of dictionaries."""
        with self._connect() as connection:
            rows = connection.execute("SELECT start, end, total_eur FROM trips").fetchall()
        return [dict(row) for row in rows]

    def count(self):
        """Return the number of saved trips."""
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) FROM trips").fetchone()
        return row[0]

    def trips_for_day(self, day=None):
        """Return the trips that started on the given day (YYYY-MM-DD). Default: today."""
        day = day or datetime.now().date().isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT start, end, total_eur FROM trips WHERE start LIKE ? ORDER BY start",
                (day + "%",),
            ).fetchall()
        return [dict(row) for row in rows]
