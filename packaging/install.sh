#!/usr/bin/env bash
# Install CleanSweep for the current user (no sudo required).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/dist/CleanSweep"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
ICON_BASE="$HOME/.local/share/icons/hicolor"
ICON_DIR="$ICON_BASE/512x512/apps"
DATA_DIR="$HOME/.local/share/cleansweep"

if [[ ! -x "$SRC" ]]; then
  echo "Missing executable: $SRC" >&2
  echo "Build it first with: packaging/build.sh" >&2
  exit 1
fi

install -d "$BIN_DIR" "$APPS_DIR" "$ICON_DIR"
rm -f "$BIN_DIR/cleansweep"
install -m 755 "$SRC" "$BIN_DIR/cleansweep"
install -m 644 "$ROOT/assets/cleansweep.png" "$ICON_DIR/cleansweep.png"

DESKTOP_FILE="$APPS_DIR/cleansweep.desktop"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=CleanSweep
GenericName=Cleaning Company Management
Comment=Manage clients, staff, payroll, stock, equipment and UK compliance
Exec=$BIN_DIR/cleansweep
Icon=$ICON_DIR/cleansweep.png
Terminal=false
Categories=Office;
Keywords=cleaning;payroll;inventory;equipment;compliance;
StartupNotify=true
EOF
chmod 644 "$DESKTOP_FILE"

# Optional desktop shortcut (only when a Desktop folder already exists).
DESKTOP_DIR="${XDG_DESKTOP_DIR:-$HOME/Desktop}"
if [[ -d "$DESKTOP_DIR" ]]; then
  install -m 755 "$DESKTOP_FILE" "$DESKTOP_DIR/cleansweep.desktop"
  if command -v gio >/dev/null 2>&1; then
    gio set "$DESKTOP_DIR/cleansweep.desktop" metadata::trusted true >/dev/null 2>&1 || true
  fi
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi
if [[ -f "$ICON_BASE/index.theme" ]] && command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$ICON_BASE" >/dev/null 2>&1 || true
fi

cat <<EOF
CleanSweep installed.

  Executable: $BIN_DIR/cleansweep
  Menu entry: $DESKTOP_FILE
  Data:       $DATA_DIR
  Log:        $DATA_DIR/cleansweep.log

Launch it from the application menu or run: cleansweep
EOF
