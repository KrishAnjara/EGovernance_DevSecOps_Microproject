#!/usr/bin/env bash
# Runs tests + Trivy (if installed) and lists evidence files. Never fabricates results.
set -uo pipefail
cd "$(dirname "$0")/.."; mkdir -p reports
python3 -m unittest discover -s tests 2>&1 | tee reports/test-output.txt | tail -3
if command -v trivy >/dev/null; then scripts/scan_trivy.sh; else echo "Trivy: PENDING (not installed)"; fi
ls -l reports
