# CleanSweep desktop build

The project can be packaged as a single self-contained Linux executable with
PyInstaller. It runs a local Waitress web server, opens the default browser, and
stores persistent data in the user's home directory.

## Requirements

- Linux x86-64 (build on the same OS family/architecture you intend to run on)
- Python 3.10+ for building
- Build virtual environment with:

```bash
python3 -m venv .build-venv
.build-venv/bin/pip install "Django>=5.1,<5.3" waitress whitenoise pyinstaller pillow
```

`whitenoise` serves the app's static files in the packaged build. The project
still runs with `python3 manage.py runserver` without it.

## Build

```bash
packaging/build.sh
```

The executable is written to `dist/CleanSweep` (about 28 MB). The build bundles:

- all Django apps, templates and static assets
- the current `db.sqlite3` as a first-run seed database
- the desktop icon in `assets/cleansweep.png`

## Install (current user, no sudo)

```bash
packaging/install.sh
```

This installs:

| Item | Path |
| --- | --- |
| Executable | `~/.local/bin/cleansweep` |
| Menu entry | `~/.local/share/applications/cleansweep.desktop` |
| Desktop shortcut | `~/Desktop/cleansweep.desktop` (when a Desktop folder exists) |
| Icon | `~/.local/share/icons/hicolor/512x512/apps/cleansweep.png` |
| Data + log | `~/.local/share/cleansweep/` |

Launch **CleanSweep** from the application menu, or run `cleansweep` in a
terminal.

## Runtime behaviour

- First launch copies the seed database to `~/.local/share/cleansweep/db.sqlite3`
  and applies migrations. If the database has no users, demo data is seeded.
- The default address is `http://127.0.0.1:8001/`. If that port is busy, the
  next free port up to 8019 is used.
- A second launch detects the running instance and opens it in the browser.
- Demo login: `demo` / `DemoPass123!` (change it in production).
- Runtime log: `~/.local/share/cleansweep/cleansweep.log`.

Override defaults with command-line flags or environment variables:

```bash
cleansweep --port 9000 --data-dir /path/to/data --no-browser
```

| Environment variable | Purpose |
| --- | --- |
| `CLEANSWEEP_PORT` | Preferred port |
| `CLEANSWEEP_DATA_DIR` | Data directory |
| `CLEANSWEEP_DB_PATH` | Explicit SQLite database path |
| `CLEANSWEEP_DEBUG` | `1` enables Django debug mode |
| `DJANGO_SECRET_KEY` | Override the bundled secret key |
| `CLEANSWEEP_EMAIL_*` / `EMAIL_HOST*` | SMTP settings for payslip email |

## Uninstall

```bash
packaging/uninstall.sh          # keeps data
packaging/uninstall.sh --purge  # removes data too
```

## Notes

- The packaged binary is Linux-only. Build separately on Windows or macOS for
  those platforms (PyInstaller does not cross-compile).
- The local server binds only to `127.0.0.1`, so it is not exposed to the
  network. Use a proper production deployment (HTTPS, DEBUG off, real secret
  key, backups) if multiple users need remote access.
- Email sending requires valid SMTP credentials; failures are reported in the UI
  instead of crashing the app.
