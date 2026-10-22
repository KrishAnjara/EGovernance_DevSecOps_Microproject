terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Credentials are NOT set here. Use `aws configure`, AWS_PROFILE or environment variables.
provider "aws" {
  region = var.aws_region
}
