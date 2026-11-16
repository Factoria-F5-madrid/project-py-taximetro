
import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, jsonify, request, render_template,
    redirect, url_for, session
)
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired

from auth import Auth
from database import TripDatabase
from taximeter import load_rates
from trip import Trip


csrf = CSRFProtect()


class LoginForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


def create_app(db_path="taximeter.db", auth_path="auth.json"):
    """Build the Flask app with authentication and trip management."""
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")

    if not secret_key:
        secret_path = os.path.join(
            os.path.dirname(__file__), ".secret_key"
        )
        if os.path.exists(secret_path):
            with open(secret_path, "r", encoding="utf-8") as file:
                secret_key = file.read().strip()

    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY environment variable or .secret_key file "
            "must be configured."
        )

    app.config.update(
        SECRET_KEY=secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,  # Local HTTP development only
    )

    csrf.init_app(app)

    database = TripDatabase(db_path)
    auth = Auth(auth_path)

    rate_stopped, rate_moving = load_rates()
    active_trip = None

    def login_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not session.get("logged_in"):
                if request.path.startswith("/trips"):
                    return jsonify({"error": "Authentication required"}), 401
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped_view

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()

        if not auth.has_password():
            return (
                "No password has been configured. "
                "Please configure one using the existing taximeter login.",
                403,
            )

        if form.validate_on_submit():
            if auth.check_password(form.password.data):
                session.clear()
                session["logged_in"] = True
                return redirect(url_for("dashboard"))

            return render_template(
                "login.html",
                form=form,
                error="Incorrect password. Please try again.",
            ), 401

        return render_template("login.html", form=form, error=None)

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/trips/start")
    @login_required
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
    @login_required
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
    @login_required
    def current_trip():
        if active_trip is None:
            return jsonify({"error": "No active trip"}), 404

        return jsonify({
            "start": active_trip.start_time,
            "state": active_trip.state,
            "current_total_eur": round(active_trip.current_total(), 2)
        })

    @app.post("/trips/finish")
    @login_required
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
    @login_required
    def list_trips():
        day = request.args.get("day")
        if day is None:
            trips = database.load()
        else:
            trips = database.trips_for_day(day)
        return jsonify(trips)

    @app.get("/trips/summary")
    @login_required
    def summary():
        day = request.args.get("day")
        trips = database.load() if day is None else database.trips_for_day(day)
        total = TripDatabase.total_of(trips)
        return jsonify({"count": len(trips), "total_eur": round(total, 2)})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
