#!/usr/bin/env bash
# Starts SonarQube + Jenkins as containers on one Linux Docker host (used by Terraform on EC2).
# Jenkins reaches SonarQube at http://sonarqube:9000 over the shared "cicd" network.
set -euo pipefail
cd "$(dirname "$0")"
DOCKER_GID="${DOCKER_GID:-$(getent group docker | cut -d: -f3)}"
docker network inspect cicd >/dev/null 2>&1 || docker network create cicd
docker rm -f jenkins sonarqube >/dev/null 2>&1 || true   # volumes (data) are kept
docker run -d --name sonarqube --network cicd --restart unless-stopped -p 9000:9000 \
  -v sonar_data:/opt/sonarqube/data -v sonar_extensions:/opt/sonarqube/extensions sonarqube:community
docker build -t egov-jenkins:local .
docker run -d --name jenkins --network cicd --restart unless-stopped -p 8080:8080 \
  --group-add "$DOCKER_GID" -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock \
  egov-jenkins:local
echo "Jenkins:   http://<host>:8080  (password: docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)"
echo "SonarQube: http://<host>:9000  (first login admin/admin, you must change it)"
