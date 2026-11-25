#!/usr/bin/env python3
"""CleanSweep desktop launcher.

Runs the Django app with a production WSGI server (waitress), stores data in a
per-user directory, applies migrations, and opens the default browser.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


APP_NAME = "CleanSweep"
DEFAULT_PORT = 8001
HOST = "127.0.0.1"


def bundled_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent


def default_data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base) / "cleansweep"
    return Path.home() / ".local" / "share" / "cleansweep"


def ensure_database(data_dir: Path, bundle: Path) -> bool:
    """Create the writable DB from the bundled demo DB. Returns True if new."""
    db_path = data_dir / "db.sqlite3"
    if db_path.exists():
        return False
    bundled_db = bundle / "db.sqlite3"
    if bundled_db.exists():
        shutil.copy2(bundled_db, db_path)
    return True


def wait_for_server(port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    url = f"http://{HOST}:{port}/health/"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    return False


def is_running(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{port}/health/", timeout=1) as response:
            return response.status == 200
    except Exception:
        return False


def open_browser_when_ready(port: int) -> None:
    if wait_for_server(port):
        webbrowser.open(f"http://{HOST}:{port}/")


def pick_port(preferred: int) -> int:
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((HOST, port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found between {preferred} and {preferred + 19}.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"{APP_NAME} desktop launcher")
    parser.add_argument("--port", type=int, default=int(os.environ.get("CLEANSWEEP_PORT", DEFAULT_PORT)))
    parser.add_argument("--data-dir", default=os.environ.get("CLEANSWEEP_DATA_DIR", str(default_data_dir())))
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser.")
    parser.add_argument("--no-migrate", action="store_true", help="Skip database migrations.")
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    # If an instance is already serving, just focus/open it.
    if is_running(args.port):
        if not args.no_browser:
            webbrowser.open(f"http://{HOST}:{args.port}/")
        print(f"{APP_NAME} is already running at http://{HOST}:{args.port}/")
        return 0

    bundle = bundled_dir()
    new_db = ensure_database(data_dir, bundle)

    os.environ["CLEANSWEEP_DATA_DIR"] = str(data_dir)
    os.environ.setdefault("CLEANSWEEP_DB_PATH", str(data_dir / "db.sqlite3"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    log_path = data_dir / "cleansweep.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
    )
    log = logging.getLogger("cleansweep")

    try:
        import django

        django.setup()
        from django.core.management import call_command
        from django.core.wsgi import get_wsgi_application

        if not args.no_migrate:
            call_command("migrate", interactive=False, verbosity=0)
        if new_db:
            try:
                from django.contrib.auth import get_user_model

                if not get_user_model().objects.exists():
                    call_command("seed_demo", verbosity=0)
            except Exception:
                log.exception("Demo seed skipped")

        application = get_wsgi_application()
        port = pick_port(args.port)

        if not args.no_browser:
            threading.Thread(target=open_browser_when_ready, args=(port,), daemon=True).start()

        from waitress import serve

        logging.getLogger("waitress").setLevel(logging.WARNING)
        print(f"{APP_NAME} running at http://{HOST}:{port}/")
        print(f"Data folder: {data_dir}")
        print("Press Ctrl+C to stop.")
        try:
            serve(application, host=HOST, port=port, threads=8, ident=APP_NAME)
        except KeyboardInterrupt:
            print("\nStopped.")
        return 0
    except Exception:
        log.exception("CleanSweep failed to start")
        print(f"CleanSweep failed to start. See log: {log_path}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
