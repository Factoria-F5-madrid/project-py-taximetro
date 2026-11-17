import time
from datetime import datetime


class Trip:
    """One taxi trip: it tracks the state, the running fare and the start time."""

    STOPPED = "stopped"
    MOVING = "moving"

    def __init__(self, rate_stopped, rate_moving):
        self.rate_stopped = rate_stopped  # EUR per second
        self.rate_moving = rate_moving    # EUR per second
        self.state = Trip.STOPPED
        self.total = 0.0
        self.last_change = time.time()
        self.start_time = datetime.now().isoformat(timespec="seconds")

    def _update_fare(self):
        """Add the cost of the time spent in the current state since the last change."""
        now = time.time()
        elapsed = now - self.last_change
        rate = self.rate_moving if self.state == Trip.MOVING else self.rate_stopped
        self.total += elapsed * rate
        self.last_change = now

    def change_state(self, new_state):
        """Switch state. Returns True if it changed, False if it was already in that state."""
        if new_state == self.state:
            return False
        self._update_fare()  # charge the previous stretch at its own rate
        self.state = new_state
        return True

    def finish(self):
        """Close the trip and return the total fare in euros."""
        self._update_fare()
        return self.total

    def current_total(self):
        """Return the fare so far, including the time since the last change (does not change the trip)."""
        rate = self.rate_moving if self.state == Trip.MOVING else self.rate_stopped
        return self.total + (time.time() - self.last_change) * rate