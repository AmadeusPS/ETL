# ---------------------------------------------------------------------------
# Azure Container Registry (replaces AWS ECR)
# ---------------------------------------------------------------------------
resource "azurerm_container_registry" "main" {
  name                = "${replace(var.project, "-", "")}${var.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"   # Use Standard/Premium for geo-replication
  admin_enabled       = true

  tags = { Project = var.project, Environment = var.environment }
}

# ---------------------------------------------------------------------------
# Log Analytics Workspace (Container Apps observability)
# ---------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project}-${var.environment}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = { Project = var.project, Environment = var.environment }
}

# ---------------------------------------------------------------------------
# Container Apps Environment (replaces ECS Cluster + ALB)
# ---------------------------------------------------------------------------
resource "azurerm_container_app_environment" "main" {
  name                       = "${var.project}-${var.environment}-env"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  infrastructure_subnet_id   = azurerm_subnet.private.id

  tags = { Project = var.project, Environment = var.environment }
}

# ---------------------------------------------------------------------------
# Container App – FastAPI (replaces ECS Service + Task Definition + ALB)
# ---------------------------------------------------------------------------
resource "azurerm_container_app" "api" {
  name                         = "${var.project}-api"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  secret {
    name  = "anthropic-api-key"
    value = var.anthropic_api_key
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.main.admin_password
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "acr-password"
  }

  template {
    min_replicas = 1
    max_replicas = 5

    container {
      name   = "api"
      image  = "${azurerm_container_registry.main.login_server}/${var.project}/api:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "DATABASE_URL"
        value = "postgresql://${var.db_username}:${var.db_password}@${azurerm_postgresql_flexible_server.main.fqdn}/pricewatch"
      }
      env {
        name  = "REDIS_URL"
        value = "rediss://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:${azurerm_redis_cache.main.ssl_port}/0"
      }
      env {
        name        = "ANTHROPIC_API_KEY"
        secret_name = "anthropic-api-key"
      }
      env {
        name  = "B2C_TENANT_NAME"
        value = var.b2c_tenant_name
      }
      env {
        name  = "B2C_CLIENT_ID"
        value = var.b2c_client_id
      }
      env {
        name  = "B2C_POLICY_NAME"
        value = var.b2c_policy_name
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "http"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = { Project = var.project, Environment = var.environment }
}

# ---------------------------------------------------------------------------
# Container App – Celery Worker (replaces ECS worker Service)
# ---------------------------------------------------------------------------
resource "azurerm_container_app" "worker" {
  name                         = "${var.project}-worker"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  secret {
    name  = "anthropic-api-key"
    value = var.anthropic_api_key
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.main.admin_password
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "acr-password"
  }

  template {
    min_replicas = 1
    max_replicas = 3

    container {
      name    = "worker"
      image   = "${azurerm_container_registry.main.login_server}/${var.project}/worker:latest"
      cpu     = 1.0
      memory  = "2Gi"
      command = ["celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info", "--concurrency=4"]

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "DATABASE_URL"
        value = "postgresql://${var.db_username}:${var.db_password}@${azurerm_postgresql_flexible_server.main.fqdn}/pricewatch"
      }
      env {
        name  = "REDIS_URL"
        value = "rediss://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:${azurerm_redis_cache.main.ssl_port}/0"
      }
      env {
        name        = "ANTHROPIC_API_KEY"
        secret_name = "anthropic-api-key"
      }
    }
  }

  tags = { Project = var.project, Environment = var.environment }
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "api_fqdn" {
  description = "Container App API URL"
  value       = "https://${azurerm_container_app.api.latest_revision_fqdn}"
}
