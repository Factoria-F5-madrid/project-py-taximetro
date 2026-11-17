import logging
import tkinter as tk
from tkinter import messagebox, simpledialog

from auth import MAX_ATTEMPTS, MIN_LENGTH, Auth
from database import TripDatabase
from taximeter import load_rates
from trip import Trip

BIG_FONT = ("Helvetica", 28, "bold")
FARE_FONT = ("Helvetica", 72, "bold")
TEXT_FONT = ("Helvetica", 18)

GREEN = "#2e7d32"
ORANGE = "#ef6c00"
BLUE = "#1565c0"
RED = "#c62828"


class TaximeterApp(tk.Tk):
    """Graphical taximeter with big buttons, a live fare and today's trips."""

    def __init__(self, rate_stopped, rate_moving, history):
        super().__init__()
        self.title("Taxi meter")
        self.geometry("720x760")
        self.rate_stopped = rate_stopped
        self.rate_moving = rate_moving
        self.history = history
        self.trip = None

        self.fare_text = tk.StringVar(value="0.00 EUR")
        self.state_text = tk.StringVar(value="No active trip")
        self.rates_text = tk.StringVar(
            value=f"Stopped: {rate_stopped} EUR/s   Moving: {rate_moving} EUR/s"
        )
        self.history_text = tk.StringVar()

        self._build_widgets()
        self._refresh_history()
        self._tick()

    def _build_widgets(self):
        tk.Label(self, textvariable=self.state_text, font=TEXT_FONT).pack(pady=(20, 0))
        tk.Label(self, textvariable=self.fare_text, font=FARE_FONT).pack(pady=10)
        tk.Label(self, textvariable=self.rates_text, font=("Helvetica", 12)).pack()

        buttons = tk.Frame(self)
        buttons.pack(pady=20, fill="x", padx=20)
        buttons.columnconfigure((0, 1), weight=1)

        self.start_button = self._big_button(buttons, "START", GREEN, self.start_trip, 0, 0)
        self.finish_button = self._big_button(buttons, "FINISH", RED, self.finish_trip, 0, 1)
        self.move_button = self._big_button(buttons, "MOVE", BLUE, lambda: self.set_state(Trip.MOVING), 1, 0)
        self.stop_button = self._big_button(buttons, "STOP", ORANGE, lambda: self.set_state(Trip.STOPPED), 1, 1)
        self._set_trip_buttons(False)

        tk.Label(self, text="Today's trips", font=("Helvetica", 16, "bold")).pack(pady=(10, 0))
        tk.Label(self, textvariable=self.history_text, font=("Helvetica", 14), justify="left").pack()

    @staticmethod
    def _big_button(parent, text, color, command, row, column):
        button = tk.Button(
            parent, text=text, font=BIG_FONT, bg=color, fg="black",
            activebackground=color, highlightbackground=color,
            height=2, command=command,
        )
        button.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
        return button

    def _set_trip_buttons(self, active):
        state = "normal" if active else "disabled"
        for button in (self.move_button, self.stop_button, self.finish_button):
            button.config(state=state)
        self.start_button.config(state="disabled" if active else "normal")

    def _tick(self):
        """Refresh the live fare five times per second."""
        if self.trip is not None:
            self.fare_text.set(f"{self.trip.current_total():.2f} EUR")
        self.after(200, self._tick)

    def _refresh_history(self):
        trips = self.history.trips_for_day()
        if not trips:
            self.history_text.set("No trips today.")
            return
        lines = [f"{n}. {t['start'][11:]} -> {t['end'][11:]}   {t['total_eur']:.2f} EUR"
                 for n, t in enumerate(trips, start=1)]
        lines.append(f"Total today: {self.history.total_of(trips):.2f} EUR")
        self.history_text.set("\n".join(lines))

    def start_trip(self):
        self.trip = Trip(self.rate_stopped, self.rate_moving)
        self.state_text.set("Taxi stopped")
        self._set_trip_buttons(True)
        logging.info("Trip started (GUI)")

    def set_state(self, new_state):
        if self.trip is not None and self.trip.change_state(new_state):
            self.state_text.set("Taxi moving" if new_state == Trip.MOVING else "Taxi stopped")
            logging.info("State changed to %s (GUI)", new_state)

    def finish_trip(self):
        if self.trip is None:
            return
        total = self.trip.finish()
        self.history.save(self.trip)
        logging.info("Trip finished. Total: %.2f EUR (GUI)", total)
        self.trip = None
        self.fare_text.set("0.00 EUR")
        self.state_text.set("No active trip")
        self._set_trip_buttons(False)
        self._refresh_history()
        messagebox.showinfo("Trip finished", f"Total to pay: {total:.2f} EUR")


def ask_login(root, auth):
    """Show password pop-ups. Returns True if access is granted."""
    if not auth.has_password():
        while True:
            password = simpledialog.askstring(
                "New password", f"Create a password (at least {MIN_LENGTH} characters):", show="*", parent=root)
            if password is None:
                return False
            if len(password) < MIN_LENGTH:
                messagebox.showwarning("Too short", "Please use a longer password.", parent=root)
                continue
            if password != simpledialog.askstring("New password", "Repeat the password:", show="*", parent=root):
                messagebox.showwarning("No match", "The passwords do not match.", parent=root)
                continue
            auth.set_password(password)
            return True

    for attempt in range(1, MAX_ATTEMPTS + 1):
        password = simpledialog.askstring("Login", "Password:", show="*", parent=root)
        if password is None:
            return False
        if auth.check_password(password):
            logging.info("Login successful (GUI)")
            return True
        logging.warning("Failed login attempt %d of %d (GUI)", attempt, MAX_ATTEMPTS)
        messagebox.showerror("Wrong password", f"Attempt {attempt} of {MAX_ATTEMPTS}.", parent=root)
    return False


def main():
    rate_stopped, rate_moving = load_rates()
    app = TaximeterApp(rate_stopped, rate_moving, TripDatabase())
    app.withdraw()  # hide the window until the login succeeds
    if ask_login(app, Auth()):
        app.deiconify()
        app.mainloop()
    else:
        app.destroy()


if __name__ == "__main__":
    main()