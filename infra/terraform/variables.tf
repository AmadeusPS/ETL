variable "azure_location" {
  description = "Azure region"
  default     = "West Europe"
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
  description = "PostgreSQL Flexible Server admin username"
  default     = "pricewatch"
  sensitive   = true
}

variable "db_password" {
  description = "PostgreSQL Flexible Server admin password"
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key stored in Azure Key Vault"
  sensitive   = true
}

variable "b2c_tenant_name" {
  description = "Azure AD B2C tenant name (without .onmicrosoft.com), e.g. pricewatchusers"
}

variable "b2c_client_id" {
  description = "Azure AD B2C frontend app registration (client) ID"
}

variable "b2c_client_secret" {
  description = "Azure AD B2C app registration client secret"
  sensitive   = true
}

variable "b2c_policy_name" {
  description = "Azure AD B2C combined sign-up/sign-in user flow name"
  default     = "B2C_1_signupsignin"
}
