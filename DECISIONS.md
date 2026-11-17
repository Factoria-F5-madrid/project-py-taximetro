# Technical decisions

This document explains the main technical decisions made in Phases 1 and 2 of the taximeter project, and why.

## How to run

```
python3 taximeter.py          # start the taximeter
python3 -m unittest -v        # run the automated tests
```

Only the Python standard library is used, so nothing has to be installed.

## Phase 1

**Time is measured with timestamps, not counters.** The program stores the moment of the last state change (`time.time()`) and, at each change, charges `elapsed seconds x rate` for the state that just ended. A loop that counts seconds would block the program while it waits for the driver's input. With timestamps the fare stays correct however long the driver takes to type.

**Fares are charged per state, at the moment of the change.** Before switching between "stopped" and "moving", the program charges the previous stretch at its own rate. That is why a trip with several changes is still calculated correctly.

**A trip is a dictionary.** It holds the current state, the time of the last change, the running total and the start time. This is enough for Phase 1 and 2. In Phase 3 it is a natural candidate to become a class.

**The main loop is separate from the logic.** Functions such as `update_fare`, `change_state` and `finish_trip` do the work, and `main()` only reads commands. This made the logic easy to test in Phase 2.

**Invalid input never crashes the program.** Unknown commands, commands without an active trip and attempts to exit during a trip print a message and are logged.

## Phase 2

**Logging with the `logging` module.** Every event (program start, trip start, state change, finish, invalid command) is written to `taximeter.log` with a timestamp and a level (INFO or WARNING). This helps diagnose problems after the fact. The log is listed in `.gitignore` because it is generated data.

**Trip history in a JSON file (`trips.json`).** Each finished trip is saved with its start time, end time and total, and the `history` command shows today's trips and their total. JSON was chosen because it is human-readable, built into Python, and easy to move to a database in Phase 4. If the file is missing or corrupted, the program starts with an empty history and logs an error instead of crashing. The file is in `.gitignore` because it holds user data.

**Fares in a config file (`config.json`).** The rates are no longer written in the code, so the client can change prices by editing one file, without touching the program. If the file is missing, invalid or contains negative rates, the program falls back to default rates and logs the problem, so a bad configuration never stops the taximeter from working.

**Automated tests with `unittest`.** There are 13 tests covering fare calculation (including a trip with state changes), config loading (valid, missing, broken and negative-rate files) and history (saving, loading and corrupted files). The clock is replaced with a fake one during the tests, so they run instantly and give the same result every time. Tests that use files work in a temporary folder, so they never touch the real data.

## Workflow

- Each feature was developed on its own branch and merged into `main` through a pull request.
- Commit messages follow the convention `feat:`, `test:`, `chore:` and `docs:`.
- Progress is tracked on the GitHub Projects Kanban board, with one column per phase.

## Phase 3

**Object-oriented design with three classes.** The program was split into modules, each with one job:
- `Trip` (`trip.py`) holds the state, the running fare and the start time of one trip. It does not print, log or touch files, so the command-line menu and the graphical interface can both use it.
- `TripHistory` (`history.py`) saves finished trips to `trips.json` and reads them back, including filtering by day.
- `Taximeter` (`taximeter.py`) runs the command-line menu and connects the other classes.

The behavior did not change during the refactor. The existing tests were adapted to the new structure and still pass, which is how we knew nothing broke. Dependencies such as the history file and the rates are passed in when an object is created, so tests can use temporary files and fake values.

**Password protection with a salted hash (`auth.py`).** The password is never stored. Only a random salt and a PBKDF2-HMAC-SHA256 hash with 200,000 iterations are saved in `auth.json`. The salt means two identical passwords produce different hashes, and the many iterations make guessing slower. The comparison uses `hmac.compare_digest`, which takes the same time whether the first or the last character differs. The password is typed with `getpass`, so it does not appear on screen. Access is closed after 3 wrong attempts. A missing or corrupted password file never grants access. `auth.json` is in `.gitignore` so it is never uploaded.

**Graphical interface with tkinter (`gui.py`).** tkinter comes with Python, so nothing has to be installed. The window has large buttons for use on a tablet, a live fare in big digits and today's trips. The buttons that do not make sense are disabled (for example, FINISH before a trip starts), so the driver cannot make a mistake. The live fare is refreshed every 200 ms with `after()`, which keeps the window responsive. It is computed by `Trip.current_total()`, which only reads the fare and does not change the trip, so the live number always matches the final fare. The window asks for the password before it is shown, with the same rules as the command-line version. Rates, history and password logic are reused from the other modules, not copied.

**Tests.** There are now 34 automated tests. The new ones cover the password logic (correct, wrong and too-short passwords, the stored file never containing the password, different salts, and missing or corrupted files) and the live fare. The window itself is not tested automatically, because that would need a screen. The logic behind it is covered by the tests for `Trip`.

**Known limitations and next steps.** The GUI buttons are grey on macOS, because tkinter ignores button background colors on that system, and a library such as customtkinter could fix that. The password has a minimum length but no other rules. Phase 4 will replace the JSON file with a database and expose the data through an API.