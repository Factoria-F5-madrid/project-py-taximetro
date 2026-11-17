import json
import logging
import os
from datetime import datetime


class TripHistory:
    """Saves finished trips to a JSON file and reads them back."""

    def __init__(self, path="trips.json"):
        self.path = path

    def load(self):
        """Return all saved trips. An empty list if the file is missing or corrupted."""
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            logging.error("History file is corrupted, starting with an empty history")
            return []

    def save(self, trip):
        """Add a finished trip (a Trip object) to the history file."""
        history = self.load()
        history.append(
            {
                "start": trip.start_time,
                "end": datetime.now().isoformat(timespec="seconds"),
                "total_eur": round(trip.total, 2),
            }
        )
        with open(self.path, "w") as file:
            json.dump(history, file, indent=2)
        logging.info("Trip saved to %s", self.path)

    def trips_for_day(self, day=None):
        """Return the trips that started on the given day (YYYY-MM-DD). Default: today."""
        day = day or datetime.now().date().isoformat()
        return [t for t in self.load() if t["start"].startswith(day)]

    @staticmethod
    def total_of(trips):
        """Return the sum of the totals of a list of saved trips."""
        return sum(t["total_eur"] for t in trips)