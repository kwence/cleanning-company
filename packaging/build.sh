#!/usr/bin/env bash
# Build the single-file CleanSweep executable with PyInstaller.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYINSTALLER="$ROOT/.build-venv/bin/pyinstaller"

if [[ ! -x "$PYINSTALLER" ]]; then
  cat >&2 <<'EOF'
PyInstaller is not available in .build-venv.
Create the build environment first:

  python3 -m venv .build-venv
  .build-venv/bin/pip install "Django>=5.1,<5.3" waitress whitenoise pyinstaller pillow
EOF
  exit 1
fi

cd "$ROOT"
"$PYINSTALLER" --noconfirm --clean cleansweep.spec

printf '\nBuilt: %s\nInstall with: packaging/install.sh\n' "$ROOT/dist/CleanSweep"
