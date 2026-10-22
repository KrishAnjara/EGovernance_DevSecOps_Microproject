// Declarative pipeline. Written for the Jenkins image in jenkins/Dockerfile.
// NOT yet executed by the author; see docs/AWS_JENKINS_SETUP_GUIDE.md.
pipeline {
  agent any
  options { timestamps(); timeout(time: 40, unit: 'MINUTES'); buildDiscarder(logRotator(numToKeepStr: '10')); disableConcurrentBuilds() }
  parameters {
    booleanParam(name: 'RUN_SONAR', defaultValue: true, description: 'Run SonarQube analysis (needs server config + credential, see guide)')
    booleanParam(name: 'FAIL_ON_HIGH', defaultValue: false, description: 'Fail the build if Trivy finds HIGH/CRITICAL issues')
    string(name: 'DEPLOY_HOST', defaultValue: '', description: 'PRIVATE IP of the app EC2 (terraform output app_private_ip). Empty = skip deploy')
  }
  environment {
    IMAGE_NAME = 'egov-sdlc-sim'
    IMAGE_TAG  = "${env.BUILD_NUMBER}"
    TRIVY_EXIT = "${params.FAIL_ON_HIGH ? '1' : '0'}"
  }
  stages {
    stage('Checkout') { steps { checkout scm; sh 'mkdir -p reports' } }
    stage('Install dependencies') {
      steps { sh 'python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt' }
    }
    stage('Automated tests') {
      steps { sh '. .venv/bin/activate && python -m pytest -v --junitxml=reports/junit.xml' }
      post { always { junit allowEmptyResults: true, testResults: 'reports/junit.xml' } }
    }
    stage('SonarQube analysis') {
      when { expression { params.RUN_SONAR } }
      steps {
        // 'SonarQube' = server name in Manage Jenkins > System (URL http://sonarqube:9000 + token credential)
        withSonarQubeEnv('SonarQube') { sh 'sonar-scanner -Dsonar.token=$SONAR_AUTH_TOKEN' }
      }
    }
    stage('Trivy filesystem scan') {
      steps {
        sh 'trivy fs --skip-dirs .venv,reports --scanners vuln,secret,misconfig --format json --output reports/trivy-fs.json .'
        sh "trivy fs --skip-dirs .venv,reports --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --exit-code ${TRIVY_EXIT} --format table --output reports/trivy-fs.txt ."
      }
    }
    stage('Docker build') { steps { sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .' } }
    stage('Trivy image scan') {
      steps {
        sh 'trivy image --format json --output reports/trivy-image.json ${IMAGE_NAME}:${IMAGE_TAG}'
        sh "trivy image --severity HIGH,CRITICAL --exit-code ${TRIVY_EXIT} --format table --output reports/trivy-image.txt ${IMAGE_NAME}:${IMAGE_TAG}"
      }
    }
    stage('Deploy to AWS EC2') {
      when { expression { params.DEPLOY_HOST?.trim() } }
      steps {
        script { if (!(params.DEPLOY_HOST ==~ /^[A-Za-z0-9.\-]+$/)) { error 'DEPLOY_HOST has invalid characters' } }
        // 'deploy-ssh-key' = SSH Username with private key credential (user: ec2-user, key = your .pem)
        sshagent(credentials: ['deploy-ssh-key']) {
          sh '''
            docker save ${IMAGE_NAME}:${IMAGE_TAG} | gzip | ssh -o StrictHostKeyChecking=accept-new ec2-user@${DEPLOY_HOST} "gunzip | sudo docker load"
            ssh -o StrictHostKeyChecking=accept-new ec2-user@${DEPLOY_HOST} \
              "sudo docker rm -f egov || true; sudo docker run -d --name egov --restart unless-stopped -p 80:8000 -v egov_data:/data ${IMAGE_NAME}:${IMAGE_TAG}"
          '''
        }
      }
    }
    stage('Post-deploy smoke test') {
      when { expression { params.DEPLOY_HOST?.trim() } }
      steps { sh 'for i in $(seq 1 10); do curl -fsS http://${DEPLOY_HOST}/healthz && exit 0; sleep 3; done; exit 1' }
    }
  }
  post { always { archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true, fingerprint: true } }
}
