import json
import os
import tempfile
import unittest

from auth import Auth


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "auth.json")
        self.auth = Auth(self.path)

    def test_no_password_at_start(self):
        self.assertFalse(self.auth.has_password())

    def test_set_password_creates_the_file(self):
        self.assertTrue(self.auth.set_password("secret1"))
        self.assertTrue(self.auth.has_password())

    def test_correct_password_passes(self):
        self.auth.set_password("secret1")
        self.assertTrue(self.auth.check_password("secret1"))

    def test_wrong_password_fails(self):
        self.auth.set_password("secret1")
        self.assertFalse(self.auth.check_password("secret2"))

    def test_password_is_case_sensitive(self):
        self.auth.set_password("secret1")
        self.assertFalse(self.auth.check_password("SECRET1"))

    def test_short_password_is_refused(self):
        self.assertFalse(self.auth.set_password("abc"))
        self.assertFalse(self.auth.has_password())

    def test_password_is_not_stored_in_plain_text(self):
        self.auth.set_password("secret1")
        with open(self.path, "r") as file:
            content = file.read()
        self.assertNotIn("secret1", content)

    def test_file_contains_only_salt_and_hash(self):
        self.auth.set_password("secret1")
        with open(self.path, "r") as file:
            data = json.load(file)
        self.assertEqual(set(data.keys()), {"salt", "hash"})

    def test_same_password_gets_different_hashes(self):
        self.auth.set_password("secret1")
        with open(self.path, "r") as file:
            first = json.load(file)
        self.auth.set_password("secret1")
        with open(self.path, "r") as file:
            second = json.load(file)
        self.assertNotEqual(first["salt"], second["salt"])
        self.assertNotEqual(first["hash"], second["hash"])

    def test_missing_file_fails_safely(self):
        self.assertFalse(self.auth.check_password("secret1"))

    def test_corrupted_file_fails_safely(self):
        with open(self.path, "w") as file:
            file.write("{ broken")
        self.assertFalse(self.auth.check_password("secret1"))


if __name__ == "__main__":
    unittest.main()