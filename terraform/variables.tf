variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "key_name" {
  description = "Name of an EXISTING EC2 key pair (create it in the AWS console first)"
  type        = string
}

variable "admin_cidr" {
  description = "Your public IP as x.x.x.x/32. Allowed to reach SSH, Jenkins (8080) and SonarQube (9000)."
  type        = string
}

variable "http_cidr" {
  description = "Who may open the demo website on port 80"
  type        = string
  default     = "0.0.0.0/0"
}

variable "repo_url" {
  description = "PUBLIC https Git URL of this project; the Jenkins server clones it to build its CI image"
  type        = string
}

variable "jenkins_instance_type" {
  description = "Jenkins + SonarQube need about 4 GB RAM. t3.small is too small for SonarQube."
  type        = string
  default     = "t3.medium"
}

variable "app_instance_type" {
  description = "Instance size for the demo web app"
  type        = string
  default     = "t3.micro"
}
