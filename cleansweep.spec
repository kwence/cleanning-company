# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the CleanSweep desktop app."""

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

PROJECT = Path(SPECPATH).resolve()
APP_NAME = "CleanSweep"

APPS = [
    "core",
    "clients",
    "employees",
    "shifts",
    "timeclock",
    "badges",
    "tasks",
    "payroll",
    "accounting",
    "banking",
    "inventory",
]

datas = []

# Bundle templates/static preserving the project-relative layout so that
# Django's APP_DIRS and staticfiles finders can locate them in frozen mode.
for app in APPS:
    for subdir in ("templates", "static"):
        root = PROJECT / app / subdir
        if not root.is_dir():
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for filename in filenames:
                if filename.endswith((".pyc", ".pyo")):
                    continue
                src = Path(dirpath) / filename
                rel = src.relative_to(PROJECT)
                datas.append((str(src), str(rel.parent)))

# Seed database copied to the per-user data folder on first launch.
if (PROJECT / "db.sqlite3").exists():
    datas.append((str(PROJECT / "db.sqlite3"), "."))

# Runtime assets (desktop icon shown in docs/about dialogs).
if (PROJECT / "assets" / "cleansweep.png").exists():
    datas.append((str(PROJECT / "assets" / "cleansweep.png"), "assets"))

hiddenimports = [
    "config.settings",
    "config.urls",
    "config.wsgi",
    "django.db.backends.sqlite3",
    "django.core.management.commands.migrate",
    "django.core.management.commands.runserver",
    "django.core.management.commands.collectstatic",
    "whitenoise",
    "whitenoise.middleware",
    "waitress",
]

for app in APPS + ["config"]:
    hiddenimports += collect_submodules(app)

block_cipher = None

a = Analysis(
    ["launcher.py"],
    pathex=[str(PROJECT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", "matplotlib", "numpy", "pandas"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT / "assets" / "cleansweep.ico"),
)
