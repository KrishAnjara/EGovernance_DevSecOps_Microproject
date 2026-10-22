#!/bin/bash
dnf install -y docker
systemctl enable --now docker
docker run -d --name egov --restart unless-stopped -p 80:8000 ${docker_image}
