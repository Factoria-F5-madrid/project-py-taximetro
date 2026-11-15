from flask import Flask, jsonify, request

from database import TripDatabase


def create_app(db_path="taximeter.db"):
    """Build the Flask app. The database path is a parameter so tests can use a temporary file."""
    app = Flask(__name__)
    database = TripDatabase(db_path)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

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
    app.run(debug=True, port=5000)