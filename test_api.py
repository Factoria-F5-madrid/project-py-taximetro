
import tempfile
import unittest
from pathlib import Path

from api import create_app


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = str(Path(self.temp_dir.name) / "test.db")

        app = create_app(db_path)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_start_trip(self):
        response = self.client.post("/trips/start")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["state"], "stopped")

    def test_cannot_start_twice(self):
        self.client.post("/trips/start")
        response = self.client.post("/trips/start")
        self.assertEqual(response.status_code, 409)

    def test_current_trip(self):
        self.client.post("/trips/start")
        response = self.client.get("/trips/current")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["state"], "stopped")
        self.assertIn("current_total_eur", response.json)

    def test_change_state(self):
        self.client.post("/trips/start")
        response = self.client.post(
            "/trips/state", json={"state": "moving"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["state"], "moving")

    def test_invalid_state(self):
        self.client.post("/trips/start")
        response = self.client.post(
            "/trips/state", json={"state": "flying"}
        )

        self.assertEqual(response.status_code, 400)

    def test_finish_trip_saves_to_database(self):
        self.client.post("/trips/start")
        response = self.client.post("/trips/finish")

        self.assertEqual(response.status_code, 200)

        trips = self.client.get("/trips").json
        self.assertEqual(len(trips), 1)
        self.assertIn("total_eur", trips[0])

    def test_finish_without_active_trip(self):
        response = self.client.post("/trips/finish")
        self.assertEqual(response.status_code, 404)

    def test_change_state_without_active_trip(self):
        response = self.client.post(
            "/trips/state", json={"state": "moving"}
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
