output "jenkins_url" {
  description = "Jenkins UI (ready about 5-8 minutes after apply)"
  value       = "http://${aws_instance.jenkins.public_ip}:8080"
}

output "sonarqube_url" {
  description = "SonarQube UI"
  value       = "http://${aws_instance.jenkins.public_ip}:9000"
}

output "app_url" {
  description = "Demo website (live after the first successful deploy from Jenkins)"
  value       = "http://${aws_instance.app.public_ip}"
}

output "app_private_ip" {
  description = "Use this as the DEPLOY_HOST build parameter in Jenkins"
  value       = aws_instance.app.private_ip
}

output "ssh_jenkins" {
  description = "SSH command for the Jenkins server (replace the key path)"
  value       = "ssh -i <path-to-your-key>.pem ec2-user@${aws_instance.jenkins.public_ip}"
}
