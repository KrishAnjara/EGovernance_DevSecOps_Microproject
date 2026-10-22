data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

data "aws_vpc" "default" {
  default = true
}

locals {
  tags = { Project = "egov-sdlc-microproject", Purpose = "academic-demo" }
}

# --- Security groups ---------------------------------------------------------
resource "aws_security_group" "jenkins" {
  name_prefix = "egov-jenkins-"
  description = "Jenkins and SonarQube, admin IP only"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH from admin"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }
  ingress {
    description = "Jenkins UI from admin"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }
  ingress {
    description = "SonarQube UI from admin"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }
  egress {
    description = "Outbound for package, image and plugin downloads"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = local.tags
  lifecycle { create_before_destroy = true }
}

resource "aws_security_group" "app" {
  name_prefix = "egov-app-"
  description = "Demo web app"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Website"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.http_cidr]
  }
  ingress {
    description     = "SSH only from the Jenkins server"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.jenkins.id]
  }
  ingress {
    description     = "Smoke test from Jenkins"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.jenkins.id]
  }
  egress {
    description = "Outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = local.tags
  lifecycle { create_before_destroy = true }
}

# --- Servers -----------------------------------------------------------------
resource "aws_instance" "jenkins" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.jenkins_instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.jenkins.id]
  user_data              = templatefile("${path.module}/jenkins_user_data.sh.tpl", { repo_url = var.repo_url })

  metadata_options { http_tokens = "required" }
  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }
  tags = merge(local.tags, { Name = "egov-jenkins-server" })
}

resource "aws_instance" "app" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.app_instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app.id]
  user_data              = file("${path.module}/app_user_data.sh.tpl")

  metadata_options { http_tokens = "required" }
  root_block_device {
    volume_size = 8
    volume_type = "gp3"
    encrypted   = true
  }
  tags = merge(local.tags, { Name = "egov-app-server" })
}
