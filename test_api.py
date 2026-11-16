
import tempfile
import unittest
from pathlib import Path

from api import create_app
from auth import Auth


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        db_path = str(Path(self.temp_dir.name) / "test.db")
        auth_path = str(Path(self.temp_dir.name) / "auth.json")

        Auth(auth_path).set_password("testpassword")

        app = create_app(db_path, auth_path)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

        self.client = app.test_client()

        with self.client.session_transaction() as session:
            session["logged_in"] = True

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

    def test_login_success(self):
        with self.client.session_transaction() as session:
            session.clear()

        response = self.client.post(
            "/login", data={"password": "testpassword"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/")

    def test_login_invalid_password(self):
        with self.client.session_transaction() as session:
            session.clear()

        response = self.client.post(
            "/login", data={"password": "wrongpassword"}
        )

        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_requires_login(self):
        with self.client.session_transaction() as session:
            session.clear()

        response = self.client.get("/trips")

        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        response = self.client.post("/logout")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/login")

        response = self.client.get("/trips")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
