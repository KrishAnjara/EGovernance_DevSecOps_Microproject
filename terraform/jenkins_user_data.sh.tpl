#!/bin/bash
# Runs once at first boot. Log: /var/log/stack-start.log
set -x
sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" > /etc/sysctl.d/99-sonarqube.conf
dnf install -y docker git
systemctl enable --now docker
git clone ${repo_url} /opt/app
cd /opt/app && bash jenkins/start_stack.sh > /var/log/stack-start.log 2>&1
