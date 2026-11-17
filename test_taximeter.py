import json
import os
import tempfile
import unittest
from unittest.mock import patch

import database
import taximeter
from history import TripHistory
from trip import Trip


class TestTrip(unittest.TestCase):
    @patch("trip.time.time")
    def test_stopped_fare(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        mock_time.return_value = 1010.0
        self.assertAlmostEqual(trip.finish(), 10 * 0.02)

    @patch("trip.time.time")
    def test_moving_fare(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        trip.change_state(Trip.MOVING)
        mock_time.return_value = 1010.0
        self.assertAlmostEqual(trip.finish(), 10 * 0.05)

    @patch("trip.time.time")
    def test_fare_across_state_change(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        mock_time.return_value = 1010.0
        trip.change_state(Trip.MOVING)
        mock_time.return_value = 1020.0
        self.assertAlmostEqual(trip.finish(), 10 * 0.02 + 10 * 0.05)

    @patch("trip.time.time")
    def test_same_state_changes_nothing(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        mock_time.return_value = 1010.0
        self.assertFalse(trip.change_state(Trip.STOPPED))
        self.assertEqual(trip.total, 0.0)
        self.assertEqual(trip.last_change, 1000.0)

    @patch("trip.time.time")
    def test_zero_seconds_costs_nothing(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        self.assertEqual(trip.finish(), 0.0)

    def test_new_trip_starts_stopped(self):
        self.assertEqual(Trip(0.02, 0.05).state, Trip.STOPPED)


class TestCurrentTotal(unittest.TestCase):
    @patch("trip.time.time")
    def test_live_fare_while_stopped(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        mock_time.return_value = 1010.0
        self.assertAlmostEqual(trip.current_total(), 10 * 0.02)

    @patch("trip.time.time")
    def test_live_fare_across_state_change(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        mock_time.return_value = 1010.0
        trip.change_state(Trip.MOVING)
        mock_time.return_value = 1020.0
        self.assertAlmostEqual(trip.current_total(), 10 * 0.02 + 10 * 0.05)

    @patch("trip.time.time")
    def test_reading_the_fare_does_not_change_the_trip(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        mock_time.return_value = 1010.0
        trip.current_total()
        self.assertEqual(trip.total, 0.0)
        self.assertEqual(trip.last_change, 1000.0)

    @patch("trip.time.time")
    def test_live_fare_matches_final_fare(self, mock_time):
        mock_time.return_value = 1000.0
        trip = Trip(0.02, 0.05)
        trip.change_state(Trip.MOVING)
        mock_time.return_value = 1008.0
        live = trip.current_total()
        self.assertAlmostEqual(live, trip.finish())


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "config.json")

    def write_config(self, text):
        with open(self.path, "w") as file:
            file.write(text)

    def defaults(self):
        return (taximeter.DEFAULT_RATE_STOPPED, taximeter.DEFAULT_RATE_MOVING)

    def test_valid_config(self):
        self.write_config(json.dumps({"rate_stopped": 0.1, "rate_moving": 0.2}))
        self.assertEqual(taximeter.load_rates(self.path), (0.1, 0.2))

    def test_missing_file_uses_defaults(self):
        self.assertEqual(taximeter.load_rates(self.path), self.defaults())

    def test_broken_json_uses_defaults(self):
        self.write_config("this is not json")
        self.assertEqual(taximeter.load_rates(self.path), self.defaults())

    def test_negative_rate_uses_defaults(self):
        self.write_config(json.dumps({"rate_stopped": -1, "rate_moving": 0.05}))
        self.assertEqual(taximeter.load_rates(self.path), self.defaults())


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "trips.json")
        self.history = TripHistory(self.path)

    def test_no_file_gives_empty_history(self):
        self.assertEqual(self.history.load(), [])

    def test_save_and_load_trip(self):
        trip = Trip(0.02, 0.05)
        trip.total = 0.456
        self.history.save(trip)
        saved = self.history.load()
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["start"], trip.start_time)
        self.assertEqual(saved[0]["total_eur"], 0.46)

    def test_two_trips_are_both_kept(self):
        self.history.save(Trip(0.02, 0.05))
        self.history.save(Trip(0.02, 0.05))
        self.assertEqual(len(self.history.load()), 2)

    def test_corrupted_file_gives_empty_history(self):
        with open(self.path, "w") as file:
            file.write("{ broken")
        self.assertEqual(self.history.load(), [])

    def test_trips_for_day_filters_by_date(self):
        with open(self.path, "w") as file:
            json.dump(
                [
                    {"start": "2026-11-05T10:00:00", "end": "2026-11-05T10:05:00", "total_eur": 1.0},
                    {"start": "2026-11-06T10:00:00", "end": "2026-11-06T10:05:00", "total_eur": 2.0},
                ],
                file,
            )
        trips = self.history.trips_for_day("2026-11-06")
        self.assertEqual(len(trips), 1)
        self.assertEqual(TripHistory.total_of(trips), 2.0)


class TestDatabase(unittest.TestCase):
    """Test the SQLite TripDatabase storage layer."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = os.path.join(self.tmp.name, "taximeter.db")
        self.db = database.TripDatabase(self.db_path)

    def test_no_file_gives_empty_database(self):
        self.assertEqual(self.db.count(), 0)
        self.assertEqual(self.db.load(), [])

    def test_save_and_load_trip(self):
        trip = Trip(0.02, 0.05)
        trip.total = 12.50
        self.db.save(trip)
        self.assertEqual(self.db.count(), 1)
        
        trips = self.db.load()
        self.assertEqual(len(trips), 1)
        self.assertEqual(trips[0]["total_eur"], 12.50)

    def test_trips_for_day_filters_by_date(self):
        trip1 = Trip(0.02, 0.05)
        trip1.start_time = "2026-11-12T08:00:00"
        trip1.total = 5.00
        
        trip2 = Trip(0.02, 0.05)
        trip2.start_time = "2026-11-13T09:00:00"
        trip2.total = 8.50

        self.db.save(trip1)
        self.db.save(trip2)
        
        day_trips = self.db.trips_for_day("2026-11-13")
        self.assertEqual(len(day_trips), 1)
        self.assertEqual(day_trips[0]["total_eur"], 8.50)

    def test_total_of_trips(self):
        trips = [
            {"total_eur": 4.00},
            {"total_eur": 6.50},
            {"total_eur": 2.25}
        ]
        self.assertEqual(database.TripDatabase.total_of(trips), 12.75)


class TestTaximeter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        history = TripHistory(os.path.join(self.tmp.name, "trips.json"))
        self.meter = taximeter.Taximeter(0.02, 0.05, history)

    def test_start_creates_a_trip(self):
        self.meter.start_trip()
        self.assertIsNotNone(self.meter.trip)

    def test_cannot_start_twice(self):
        self.meter.start_trip()
        first_trip = self.meter.trip
        self.meter.start_trip()
        self.assertIs(self.meter.trip, first_trip)

    def test_finish_saves_trip_and_clears_it(self):
        self.meter.start_trip()
        self.meter.finish_trip()
        self.assertIsNone(self.meter.trip)
        self.assertEqual(len(self.meter.history.load()), 1)

    def test_finish_without_trip_saves_nothing(self):
        self.meter.finish_trip()
        self.assertEqual(self.meter.history.load(), [])


if __name__ == "__main__":
    unittest.main()