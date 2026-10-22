#!/usr/bin/env bash
# Usage: scripts/scan_trivy.sh [image-name]   Requires: trivy (https://trivy.dev). Writes real output to reports/.
set -euo pipefail
cd "$(dirname "$0")/.."; mkdir -p reports
command -v trivy >/dev/null || { echo "trivy not installed - scan PENDING"; exit 1; }
D=$(date +%Y%m%d-%H%M%S)
trivy fs --scanners vuln,secret,misconfig --format json  --output "reports/trivy-fs-$D.json" .
trivy fs --scanners vuln,secret,misconfig --format table --output "reports/trivy-fs-$D.txt" .
if [ "${1:-}" != "" ]; then
  trivy image --format json  --output "reports/trivy-image-$D.json" "$1"
  trivy image --format table --output "reports/trivy-image-$D.txt" "$1"
fi
echo "Reports written to reports/ (scan date: $D). Copy real findings into docs/vulnerability_report_template.md"
