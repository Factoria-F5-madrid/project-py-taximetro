import json
import logging

from database import TripDatabase
from auth import Auth
from trip import Trip

CONFIG_FILE = "config.json"

# Used only if config.json is missing or invalid
DEFAULT_RATE_STOPPED = 0.02
DEFAULT_RATE_MOVING = 0.05

# Every event is written to taximeter.log with date and time
logging.basicConfig(
    filename="taximeter.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_rates(path=CONFIG_FILE):
    """Read the fares (EUR per second) from the config file, or use the defaults."""
    try:
        with open(path, "r") as file:
            config = json.load(file)
        rate_stopped = float(config["rate_stopped"])
        rate_moving = float(config["rate_moving"])
        if rate_stopped < 0 or rate_moving < 0:
            raise ValueError("rates cannot be negative")
        logging.info("Rates loaded from %s", path)
        return rate_stopped, rate_moving
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        logging.error("Could not load %s (%s). Using default rates", path, error)
        return DEFAULT_RATE_STOPPED, DEFAULT_RATE_MOVING


class Taximeter:
    """The command-line taximeter: reads commands and manages the active trip."""

    def __init__(self, rate_stopped, rate_moving, history):
        self.rate_stopped = rate_stopped
        self.rate_moving = rate_moving
        self.history = history
        self.trip = None  # None means there is no active trip

    def show_instructions(self):
        print("\n=== TAXI METER ===")
        print("Commands:")
        print("  start   -> begin a new trip")
        print(f"  stop    -> taxi is stopped (low rate: {self.rate_stopped} EUR/s)")
        print(f"  move    -> taxi is moving  (high rate: {self.rate_moving} EUR/s)")
        print("  finish  -> end the trip and show the total")
        print("  history -> show today's trips")
        print("  exit    -> close the program")

    def start_trip(self):
        if self.trip is not None:
            print("A trip is already active!")
            logging.warning("Start requested while a trip was active")
            return
        self.trip = Trip(self.rate_stopped, self.rate_moving)
        print("Trip started! The taxi is stopped.")
        logging.info("Trip started")

    def set_state(self, new_state):
        if self.trip is None:
            print("No active trip. Type 'start' first.")
            logging.warning("'%s' requested with no active trip", new_state)
            return
        if self.trip.change_state(new_state):
            print(f"State changed to: {new_state}")
            logging.info("State changed to %s", new_state)
        else:
            print(f"The taxi is already {new_state}.")
            logging.warning("Tried to set state to %s but it was already %s", new_state, new_state)

    def finish_trip(self):
        if self.trip is None:
            print("No active trip to finish.")
            logging.warning("Finish requested with no active trip")
            return
        total = self.trip.finish()
        print(f"\nTrip finished. Total to pay: {total:.2f} EUR")
        logging.info("Trip finished. Total: %.2f EUR", total)
        self.history.save(self.trip)
        self.trip = None  # ready for the next trip without closing the program

    def show_history(self):
        trips = self.history.trips_for_day()
        if not trips:
            print("No trips today.")
            return
        print("\n--- Today's trips ---")
        for number, trip in enumerate(trips, start=1):
            print(f"{number}. {trip['start'][11:]} -> {trip['end'][11:]}  {trip['total_eur']:.2f} EUR")
        print(f"Total today: {self.history.total_of(trips):.2f} EUR")

    def run(self):
        logging.info("Program started")
        self.show_instructions()
        while True:
            command = input("\n> ").strip().lower()

            if command == "start":
                self.start_trip()
            elif command == "stop":
                self.set_state(Trip.STOPPED)
            elif command == "move":
                self.set_state(Trip.MOVING)
            elif command == "finish":
                self.finish_trip()
            elif command == "history":
                self.show_history()
            elif command == "exit":
                if self.trip is not None:
                    print("Finish the active trip before exiting.")
                    logging.warning("Exit requested while a trip was active")
                else:
                    print("Goodbye!")
                    logging.info("Program closed")
                    break
            else:
                print("Invalid command.")
                logging.warning("Invalid command: %s", command)
                self.show_instructions()


def main():
    if not Auth().login():
        return  # wrong password: do not show the menu
    rate_stopped, rate_moving = load_rates()
    Taximeter(rate_stopped, rate_moving, TripDatabase()).run()


if __name__ == "__main__":
    main()