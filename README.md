# Comparative Analysis of Waterfall, Incremental and Agile Models for an E-Governance System
DevSecOps Lab microproject (B.Tech) | SDG 9: Industry, Innovation and Infrastructure
Student: [Name] | Roll no.: [Roll] | Guide: [Faculty]

**This is an academic simulation.** It is not a real government service, collects no real citizen data, and has no affiliation with any government agency.

## Stack
Flask + SQLite, plain HTML/CSS/JS, Docker (gunicorn), Jenkins, SonarQube, Trivy, Terraform (AWS EC2).

## 1. Run locally (no Docker, no AWS)
Needs Python 3.10+ (tested with 3.12).
```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python wsgi.py
```
Open http://127.0.0.1:5000 . Health check: http://127.0.0.1:5000/healthz

## 2. Tests
```bash
python -m pytest -v                       # after installing requirements-dev.txt
python -m unittest discover -s tests -v   # works without pytest
```

## 3. Docker
```bash
docker build -t egov-sdlc-sim:local .
docker run -d --name egov -p 8000:8000 -v egov_data:/data egov-sdlc-sim:local
docker ps                      # status (shows health)
docker logs egov               # inspect logs
docker inspect --format '{{.State.Health.Status}}' egov
docker stop egov && docker rm egov
```
Or with Compose: `docker compose up --build -d` then `docker compose down`. Open http://localhost:8000

## 4. Security scans (real results only)
```bash
scripts/scan_trivy.sh egov-sdlc-sim:local      # needs Trivy installed
export SONAR_HOST_URL=http://localhost:9000 SONAR_TOKEN=<token>
scripts/scan_sonar.sh                          # needs a SonarQube server
```
Output goes to `reports/`. Record results in `docs/vulnerability_report_template.md`. **All scans are PENDING until you run them.**

## 5. Host on AWS with Jenkins CI/CD (main deliverable)
Terraform creates two EC2 servers: one runs Jenkins + SonarQube (containers), the other runs the app. The Jenkins pipeline tests, scans, builds and deploys the app. **Full step-by-step guide with explanations: `docs/AWS_JENKINS_SETUP_GUIDE.md`.** This creates billable resources; run `terraform destroy` afterwards. Credentials stay outside the repo (`aws configure --profile`); IAM policy: `docs/iam-policy-terraform.json`.
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # edit key_name, admin_cidr, repo_url
terraform fmt
terraform init
terraform validate
terraform plan -out tfplan
terraform apply tfplan
terraform output
# ... follow the guide: configure Jenkins, run the pipeline ...
terraform destroy
```
Other docs: `docs/ARCHITECTURE_DECISIONS.md`, `docs/THREAT_MODEL.md`, `docs/JENKINS_SETUP.md`. `make test`, `make docker-build` etc. are shortcuts (see `Makefile`).

## Layout
`app/` Flask app, templates, static | `tests/` | `scripts/` | `terraform/` + `jenkins/` (Jenkins image and stack start script) | `docs/` (diagrams, task list, report/presentation outlines, checklist) | `reports/` (scan evidence)

## Verification status
See the end of the delivery message; items not run by the author are listed there and are your responsibility to run.
