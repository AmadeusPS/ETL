variable "aws_region" {
  description = "AWS region"
  default     = "eu-west-1"
}

variable "project" {
  description = "Project name prefix"
  default     = "pricewatch"
}

variable "environment" {
  description = "Deployment environment"
  default     = "production"
}

variable "db_username" {
  description = "RDS master username"
  default     = "pricewatch"
  sensitive   = true
}

variable "db_password" {
  description = "RDS master password"
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key stored in SSM"
  sensitive   = true
}
