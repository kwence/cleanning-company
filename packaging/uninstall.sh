#!/usr/bin/env bash
# Remove the CleanSweep installation. Data is kept unless --purge is passed.
set -euo pipefail

PURGE=0
if [[ "${1:-}" == "--purge" ]]; then
  PURGE=1
fi

BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
ICON_BASE="$HOME/.local/share/icons/hicolor"
DATA_DIR="$HOME/.local/share/cleansweep"

rm -f "$BIN_DIR/cleansweep"
rm -f "$APPS_DIR/cleansweep.desktop"
rm -f "$ICON_BASE/512x512/apps/cleansweep.png"
DESKTOP_DIR="${XDG_DESKTOP_DIR:-$HOME/Desktop}"
rm -f "$DESKTOP_DIR/cleansweep.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi
if [[ -f "$ICON_BASE/index.theme" ]] && command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$ICON_BASE" >/dev/null 2>&1 || true
fi

if [[ "$PURGE" -eq 1 ]]; then
  rm -rf "$DATA_DIR"
  echo "CleanSweep removed, including data in $DATA_DIR."
else
  echo "CleanSweep removed. Data kept in $DATA_DIR (use --purge to delete it)."
fi
