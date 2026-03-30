# ---------------------------------------------------------------------------
# Azure AD B2C Directory (replaces AWS Cognito User Pool)
#
# IMPORTANT – Post-provisioning steps (do once in Azure Portal or az CLI):
#
# 1. Switch to the new B2C tenant directory in the Portal
#
# 2. Create a custom attribute:
#    Azure AD B2C > User attributes > Add
#    Name: plan  Type: String
#
# 3. Create User Flows:
#    a) Sign up / Sign in  → name: B2C_1_signupsignin
#       - Include "plan" attribute in the flow (collect + return)
#    b) Password reset     → name: B2C_1_passwordreset
#
# 4. Register the frontend app:
#    Azure AD B2C > App registrations > New registration
#    - Name: pricewatch-frontend
#    - Account types: "Accounts in any identity provider or organizational directory"
#    - Redirect URIs (SPA): https://app.pricewatch.pt/dashboard
#                           http://localhost:3000/dashboard
#    - Enable ID tokens (implicit flow) under Authentication
#    - Copy the Application (client) ID → use as b2c_client_id variable
#
# 5. Add the "plan" claim to the token:
#    User flows > B2C_1_signupsignin > Application claims > Add claim > plan
# ---------------------------------------------------------------------------

resource "azurerm_aadb2c_directory" "main" {
  country_code            = "PT"
  data_residency_location = "Europe"
  display_name            = "PriceWatch Users"
  domain_name             = "${var.project}users.onmicrosoft.com"
  resource_group_name     = azurerm_resource_group.main.name
  sku_name                = "PremiumP1"  # Required for custom attributes

  tags = { Project = var.project, Environment = var.environment }
}

output "b2c_tenant_id" {
  description = "Azure AD B2C tenant ID (use in backend B2C_TENANT_ID env var)"
  value       = azurerm_aadb2c_directory.main.tenant_id
}

output "b2c_domain" {
  description = "Azure AD B2C tenant domain"
  value       = azurerm_aadb2c_directory.main.domain_name
}

output "b2c_authority" {
  description = "MSAL authority URL for the frontend"
  value       = "https://${var.project}users.b2clogin.com/${var.project}users.onmicrosoft.com/${var.b2c_policy_name}"
}
