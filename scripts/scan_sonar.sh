#!/usr/bin/env bash
# Requires a running SonarQube server and: export SONAR_HOST_URL=... SONAR_TOKEN=...
# Local server:  docker run -d --name sonarqube -p 9000:9000 sonarqube:community
set -euo pipefail
cd "$(dirname "$0")/.."
: "${SONAR_HOST_URL:?set SONAR_HOST_URL}"; : "${SONAR_TOKEN:?set SONAR_TOKEN}"
if command -v sonar-scanner >/dev/null; then
  sonar-scanner -Dsonar.host.url="$SONAR_HOST_URL" -Dsonar.token="$SONAR_TOKEN"
else
  docker run --rm --network host -e SONAR_HOST_URL -e SONAR_TOKEN -v "$PWD:/usr/src" sonarsource/sonar-scanner-cli
fi
echo "View results at $SONAR_HOST_URL/dashboard?id=egov-sdlc-microproject"
