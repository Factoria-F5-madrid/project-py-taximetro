from datetime import datetime

from flask import Flask, jsonify, request, render_template

from database import TripDatabase
from taximeter import load_rates
from trip import Trip


def create_app(db_path="taximeter.db"):
    """Build the Flask app with trip management and dashboard endpoints."""
    app = Flask(__name__)
    database = TripDatabase(db_path)

    rate_stopped, rate_moving = load_rates()
    active_trip = None

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/trips/start")
    def start_trip():
        nonlocal active_trip

        if active_trip is not None:
            return jsonify({"error": "A trip is already active"}), 409

        active_trip = Trip(rate_stopped, rate_moving)

        return jsonify({
            "message": "Trip started",
            "state": active_trip.state,
            "start": active_trip.start_time
        }), 201

    @app.post("/trips/state")
    def change_state():
        if active_trip is None:
            return jsonify({"error": "No active trip"}), 404

        data = request.get_json(silent=True) or {}
        new_state = data.get("state")

        if new_state not in (Trip.STOPPED, Trip.MOVING):
            return jsonify({
                "error": "State must be 'stopped' or 'moving'"
            }), 400

        if not active_trip.change_state(new_state):
            return jsonify({
                "message": "Trip is already in that state",
                "state": active_trip.state
            }), 200

        return jsonify({
            "message": "State changed",
            "state": active_trip.state,
            "current_total_eur": round(active_trip.current_total(), 2)
        }), 200

    @app.get("/trips/current")
    def current_trip():
        if active_trip is None:
            return jsonify({"error": "No active trip"}), 404

        return jsonify({
            "start": active_trip.start_time,
            "state": active_trip.state,
            "current_total_eur": round(active_trip.current_total(), 2)
        })

    @app.post("/trips/finish")
    def finish_trip():
        nonlocal active_trip

        if active_trip is None:
            return jsonify({"error": "No active trip"}), 404

        total = active_trip.finish()
        finished_trip = {
            "start": active_trip.start_time,
            "end": datetime.now().isoformat(timespec="seconds"),
            "total_eur": round(total, 2)
        }

        database.save(finished_trip)
        active_trip = None

        return jsonify({
            "message": "Trip finished",
            "total_eur": round(total, 2)
        }), 200

    @app.get("/trips")
    def list_trips():
        day = request.args.get("day")
        if day is None:
            trips = database.load()
        else:
            trips = database.trips_for_day(day)
        return jsonify(trips)

    @app.get("/trips/summary")
    def summary():
        day = request.args.get("day")
        trips = database.load() if day is None else database.trips_for_day(day)
        total = TripDatabase.total_of(trips)
        return jsonify({"count": len(trips), "total_eur": round(total, 2)})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
