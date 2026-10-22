# Jenkins controller image with every tool the pipeline needs (Python, Docker CLI, Trivy, sonar-scanner, ssh).
FROM jenkins/jenkins:lts-jdk17
ARG TRIVY_VERSION=v0.58.1
ARG SCANNER_VERSION=6.2.1.4610
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      docker.io python3 python3-venv python3-pip openssh-client curl wget unzip ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/${TRIVY_VERSION}/contrib/install.sh \
      | sh -s -- -b /usr/local/bin ${TRIVY_VERSION}
RUN wget -q -O /tmp/scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SCANNER_VERSION}-linux-x64.zip \
 && unzip -q /tmp/scanner.zip -d /opt && mv /opt/sonar-scanner-* /opt/sonar-scanner && rm /tmp/scanner.zip \
 && ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner
USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator git credentials-binding junit ssh-agent sonar timestamper pipeline-stage-view
