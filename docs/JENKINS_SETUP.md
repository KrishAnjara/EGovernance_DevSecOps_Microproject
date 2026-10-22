# Jenkins setup
The full, current procedure (AWS, Jenkins, SonarQube, credentials, pipeline job) is in **AWS_JENKINS_SETUP_GUIDE.md**.
Required plugins are pre-installed by `jenkins/Dockerfile`: Pipeline, Git, Credentials Binding, JUnit, SSH Agent, SonarQube Scanner, Timestamper, Pipeline Stage View.
Credential IDs used by the Jenkinsfile: `deploy-ssh-key` (SSH key) and the SonarQube server named `SonarQube` (with a secret-text token). The pipeline has not been executed by the author.
