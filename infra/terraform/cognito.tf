# ---------------------------------------------------------------------------
# Cognito User Pool
# ---------------------------------------------------------------------------
resource "aws_cognito_user_pool" "main" {
  name = "${var.project}-users"

  auto_verified_attributes = ["email"]
  username_attributes      = ["email"]

  password_policy {
    minimum_length    = 8
    require_uppercase = true
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
  }

  schema {
    name                = "plan"
    attribute_data_type = "String"
    mutable             = true
    string_attribute_constraints {
      min_length = 1
      max_length = 32
    }
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  tags = { Project = var.project, Environment = var.environment }
}

# Plan groups
resource "aws_cognito_user_group" "basic" {
  name         = "basic"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Basic plan"
}

resource "aws_cognito_user_group" "pro" {
  name         = "pro"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Pro plan"
}

resource "aws_cognito_user_group" "enterprise" {
  name         = "enterprise"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Enterprise plan"
}

# App client (used by Next.js frontend)
resource "aws_cognito_user_pool_client" "frontend" {
  name         = "${var.project}-frontend"
  user_pool_id = aws_cognito_user_pool.main.id

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
  ]

  generate_secret = false  # Public client (SPA)

  callback_urls = ["https://app.pricewatch.pt/dashboard", "http://localhost:3000/dashboard"]
  logout_urls   = ["https://app.pricewatch.pt/login", "http://localhost:3000/login"]

  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  allowed_oauth_flows_user_pool_client = true
  supported_identity_providers         = ["COGNITO"]
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  value = aws_cognito_user_pool_client.frontend.id
}
