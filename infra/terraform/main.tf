terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use S3 backend for state in production
  # backend "s3" {
  #   bucket = "pricewatch-terraform-state"
  #   key    = "production/terraform.tfstate"
  #   region = "eu-west-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------
# VPC (simplified – customize subnets/AZs for production HA)
# ---------------------------------------------------------------------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true  # Set false for HA in production
  enable_dns_hostnames = true
}

# ---------------------------------------------------------------------------
# SSM Parameter Store – secrets (avoid hardcoding in ECS task defs)
# ---------------------------------------------------------------------------
resource "aws_ssm_parameter" "anthropic_api_key" {
  name  = "/${var.project}/${var.environment}/anthropic_api_key"
  type  = "SecureString"
  value = var.anthropic_api_key
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/${var.project}/${var.environment}/db_password"
  type  = "SecureString"
  value = var.db_password
}
