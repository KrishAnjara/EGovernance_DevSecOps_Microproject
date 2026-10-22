# AWS + Jenkins setup guide (step by step, with explanations)

**Status:** written by the author but NOT executed against a real AWS account, Jenkins or SonarQube. Expect to troubleshoot; see section 10. Record your own real results and screenshots.

## 0. What you will build
```
You (laptop) --git push--> GitHub (public repo)
Terraform --creates--> AWS default VPC
   +-- EC2 "jenkins-server" (t3.medium): Docker -> [Jenkins container] + [SonarQube container]
   +-- EC2 "app-server" (t3.micro): Docker -> [egov web app container, port 80]
Jenkins pipeline: test -> Sonar -> Trivy -> docker build -> Trivy image -> ship image over SSH -> run -> smoke test
```
**Why two servers?** CI tools and the app should not share a machine: a compromised or overloaded build server must not take the website down, and the app server gets a minimal attack surface (port 80 plus SSH only from Jenkins).
**Why no Docker registry?** The pipeline copies the image with `docker save | ssh | docker load`, so you need no Docker Hub account or registry credentials. Trade-off: it does not scale to many servers (see ARCHITECTURE_DECISIONS.md).

## 1. Prerequisites
- AWS account with billing alerts enabled. **This costs money** while running (two EC2 instances, 38 GB EBS, public IPv4 addresses). Check the AWS pricing page; destroy when done (step 12).
- Installed on your laptop: Git, Terraform >= 1.5, AWS CLI v2.
- A GitHub account; the repo must be **public** so the Jenkins server can clone it at boot (private repos need a token; not covered).

## 2. Create a limited AWS user (least privilege)
1. AWS Console > IAM > Policies > Create policy > JSON; paste `docs/iam-policy-terraform.json`; name it `egov-terraform`.
2. IAM > Users > Create user `egov-terraform-user`; attach only that policy (no console access).
3. Create an access key for the CLI. Run `aws configure --profile egov` and enter it. The key stays in `~/.aws/credentials`, never in the repo. Then: `export AWS_PROFILE=egov` (Windows PowerShell: `$env:AWS_PROFILE="egov"`).
The policy is a starting point: if Terraform reports `UnauthorizedOperation`, the error names the missing action; add only that action.
**Why:** Terraform acts with whatever permissions you give it; a leaked admin key is far worse than a leaked EC2-only key.

## 3. Create an EC2 key pair
EC2 > Key Pairs > Create (RSA, `.pem`), name e.g. `egov-key`, in the same region as `aws_region` (default `ap-south-1`). Save the `.pem` safely; `chmod 400 egov-key.pem`.
**Why:** this key lets you SSH into Jenkins, and Jenkins uses the same key to SSH into the app server.

## 4. Push the project to GitHub
```bash
git init && git add . && git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```
Check `git status` shows no `.env`, `.tfvars`, `.tfstate` or `.pem` files (they are git-ignored).

## 5. Provision AWS with Terraform
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars    # edit key_name, admin_cidr (your IP/32), repo_url
terraform fmt
terraform init
terraform validate
terraform plan -out tfplan
terraform apply tfplan
```
Read the plan before applying: it should show 2 instances and 2 security groups. Save the outputs (`terraform output`). **Evidence:** screenshot the plan and the EC2 console.
**What the code does:** `main.tf` builds security groups (Jenkins/Sonar reachable only from your IP; app port 80 public; app SSH only from the Jenkins security group), two encrypted EC2 instances with IMDSv2 enforced; `jenkins_user_data.sh.tpl` installs Docker, clones your repo and runs `jenkins/start_stack.sh`.

## 6. Wait, then open Jenkins
Boot scripts need about 5-8 minutes (image build, plugin download). Check progress:
```bash
ssh -i egov-key.pem ec2-user@<jenkins_public_ip>
sudo tail -f /var/log/stack-start.log
docker ps          # expect containers: jenkins, sonarqube
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
Open `jenkins_url` (port 8080), paste the password, choose **Install suggested plugins** (our image already has the extras), create your admin user.
If your IP changed, update `admin_cidr` and re-apply.

## 7. Configure SonarQube
1. Open `sonarqube_url` (port 9000). Login `admin` / `admin`, set a new password when asked.
2. My Account > Security > Generate token (type: User or Global Analysis). Copy it once.
3. Jenkins > Manage Jenkins > Credentials > System > Global > Add: kind **Secret text**, ID `sonar-token`, paste the token.
4. Manage Jenkins > System > **SonarQube servers** > Add: Name `SonarQube` (must match the Jenkinsfile), URL `http://sonarqube:9000` (container name on the shared Docker network), Server authentication token = `sonar-token`. Save.
(Optional quality-gate webhook: in SonarQube, Administration > Configuration > Webhooks > URL `http://jenkins:8080/sonarqube-webhook/`. The Jenkinsfile does not wait for the gate by default.)

## 8. Add the deploy credential
Jenkins > Manage Jenkins > Credentials > Global > Add: kind **SSH Username with private key**, ID `deploy-ssh-key`, username `ec2-user`, Private key > Enter directly > paste the entire `.pem` contents.
**Why:** `sshagent` loads this key only for the deploy stage; it is never printed in logs.

## 9. Create and run the pipeline
1. New Item > name `egov-pipeline` > **Pipeline** > OK.
2. Pipeline > Definition: *Pipeline script from SCM* > Git > your repo URL > branch `*/main` > Script Path `Jenkinsfile` > Save.
3. **Build with Parameters**: keep `RUN_SONAR` on, set `DEPLOY_HOST` = `terraform output app_private_ip`. First run: leave `FAIL_ON_HIGH` off so you can read findings; later enable it to demonstrate a security gate.
4. Watch the Stage View. Expected stages: Checkout, Install dependencies, Automated tests, SonarQube analysis, Trivy filesystem scan, Docker build, Trivy image scan, Deploy to AWS EC2, Post-deploy smoke test.
5. Open `app_url` in a browser (port 80). Download the archived `reports/` artifacts (Trivy JSON/text, JUnit).
**Evidence screenshots (real only):** Jenkins stage view (green and any failed run), console output, Test Results, SonarQube dashboard, Trivy reports, the running website on the AWS IP, EC2 console.

## 10. Troubleshooting
| Symptom | Likely cause / fix |
|---|---|
| Jenkins page not loading | Wait longer; `sudo tail /var/log/stack-start.log`; IP changed vs `admin_cidr` |
| `docker: permission denied` in a build | Docker group id mismatch: re-run `DOCKER_GID=$(getent group docker \| cut -d: -f3) bash /opt/app/jenkins/start_stack.sh` |
| SonarQube container exits | `vm.max_map_count` not set or instance too small (needs ~4 GB) |
| Sonar stage: server not found | Server name must be exactly `SonarQube`; URL `http://sonarqube:9000` |
| Deploy: Permission denied (publickey) | Wrong key pair or credential ID/username |
| Deploy: connection timed out | `DEPLOY_HOST` must be the app's **private** IP; check security groups |
| Trivy slow first time | It downloads its vulnerability database (needs internet) |
| Docker build in Jenkins fails on base image pull | Docker Hub rate limits; retry later |
| Image/plugin version errors | Pinned versions (Trivy, scanner, plugins) may have moved; adjust `ARG`s in `jenkins/Dockerfile` |

## 11. Security notes
Jenkins and SonarQube are plain HTTP and limited by IP, not by TLS; Jenkins has access to the Docker socket (equivalent to root on that host), which is acceptable for a short-lived lab but not for production. Never leave the stack running unattended.

## 12. Tear down (do not skip)
```bash
cd terraform && terraform destroy
```
Confirm in the EC2 console that no instances or volumes remain. Optionally delete the IAM access key and the key pair.

## 13. Explanation of each pipeline stage (for your viva)
- **Checkout:** pulls the exact commit, giving traceability.
- **Install dependencies:** isolated virtualenv, reproducible with pinned `requirements*.txt`.
- **Automated tests:** shift-left; fails fast on regression; JUnit XML is shown in Jenkins.
- **SonarQube (SAST):** static analysis of source for bugs, code smells and security hotspots.
- **Trivy filesystem:** dependency vulnerabilities (SCA), leaked secrets and misconfigurations (Dockerfile, Terraform).
- **Docker build:** immutable artifact tagged with the build number.
- **Trivy image:** vulnerabilities in the OS packages and libraries inside the final image.
- **Deploy:** ships that same tested image (no rebuild on the server), replaces the old container.
- **Smoke test:** proves the deployed app answers `/healthz`.
- **Post actions:** archive reports regardless of outcome, as audit evidence.
