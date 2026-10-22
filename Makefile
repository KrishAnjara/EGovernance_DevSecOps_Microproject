.PHONY: run test docker-build docker-run docker-stop scan tf-check
run:          ; python3 wsgi.py
test:         ; python3 -m unittest discover -s tests -v
docker-build: ; docker build -t egov-sdlc-sim:local .
docker-run:   ; docker run -d --name egov -p 8000:8000 -v egov_data:/data egov-sdlc-sim:local
docker-stop:  ; docker rm -f egov
scan:         ; scripts/scan_trivy.sh egov-sdlc-sim:local
tf-check:     ; cd terraform && terraform fmt -check && terraform init -backend=false && terraform validate
