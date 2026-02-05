#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN=${1:-python3.14}
VENV_DIR=${2:-.venv}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "python binary '$PYTHON_BIN' not found. Please install Python 3.14 or provide a path to a 3.14 interpreter."
  echo "On macOS you can use: brew install pyenv && pyenv install 3.14.0"
  exit 1
fi

ver=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$ver" != "3.14" ]; then
  echo "Found Python $ver at '$PYTHON_BIN' but require Python 3.14." 
  exit 1
fi

echo "Using $PYTHON_BIN (version $ver) to create virtualenv in $VENV_DIR"
$PYTHON_BIN -m venv "$VENV_DIR"

echo "Activating venv and upgrading pip..."
"$VENV_DIR/bin/pip" install -U pip setuptools wheel


echo "Installing dependencies from pyproject.toml (editable mode)..."
"$VENV_DIR/bin/pip" install -e .

echo "Done. Activate with: source $VENV_DIR/bin/activate"
