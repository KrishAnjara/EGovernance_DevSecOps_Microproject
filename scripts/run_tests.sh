#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports
if python3 -m pytest --version >/dev/null 2>&1; then python3 -m pytest -v
else echo "pytest not installed; falling back to unittest"; python3 -m unittest discover -s tests -v; fi
