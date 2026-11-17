import getpass
import hashlib
import hmac
import json
import logging
import os

AUTH_FILE = "auth.json"
ITERATIONS = 200_000   # more iterations make every password guess slower
MIN_LENGTH = 6
MAX_ATTEMPTS = 3


class Auth:
    """Password protection. Only a salt and a hash are stored, never the password."""

    def __init__(self, path=AUTH_FILE):
        self.path = path

    @staticmethod
    def _hash(password, salt):
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)

    def has_password(self):
        return os.path.exists(self.path)

    def set_password(self, password):
        """Save a new password. Returns False if it is too short."""
        if len(password) < MIN_LENGTH:
            return False
        salt = os.urandom(16)  # random salt, different for every password
        data = {"salt": salt.hex(), "hash": self._hash(password, salt).hex()}
        with open(self.path, "w") as file:
            json.dump(data, file)
        logging.info("Password created")
        return True

    def check_password(self, password):
        """Return True if the password matches the stored hash."""
        try:
            with open(self.path, "r") as file:
                data = json.load(file)
            salt = bytes.fromhex(data["salt"])
            stored_hash = bytes.fromhex(data["hash"])
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            logging.error("Password file is missing or corrupted")
            return False
        return hmac.compare_digest(self._hash(password, salt), stored_hash)

    def login(self):
        """Ask for the password (creating one the first time). Returns True if access is granted."""
        if not self.has_password():
            print("No password set yet. Create one to protect the taximeter.")
            while True:
                password = getpass.getpass(f"New password (at least {MIN_LENGTH} characters): ")
                if len(password) < MIN_LENGTH:
                    print("Too short, try again.")
                    continue
                if password != getpass.getpass("Repeat the password: "):
                    print("The passwords do not match, try again.")
                    continue
                self.set_password(password)
                print("Password saved.")
                return True

        for attempt in range(1, MAX_ATTEMPTS + 1):
            if self.check_password(getpass.getpass("Password: ")):
                logging.info("Login successful")
                return True
            print(f"Wrong password ({attempt}/{MAX_ATTEMPTS}).")
            logging.warning("Failed login attempt %d of %d", attempt, MAX_ATTEMPTS)
        print("Too many failed attempts. Closing the program.")
        return False