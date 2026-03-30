# ---------------------------------------------------------------------------
# Azure Cache for Redis (replaces AWS ElastiCache)
# ---------------------------------------------------------------------------
resource "azurerm_redis_cache" "main" {
  name                = "${var.project}-${var.environment}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 1
  family              = "C"
  sku_name            = "Basic"  # Use Standard/Premium for production HA + persistence

  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {}

  tags = { Project = var.project, Environment = var.environment }
}

output "redis_hostname" {
  value = azurerm_redis_cache.main.hostname
}

output "redis_ssl_port" {
  value = azurerm_redis_cache.main.ssl_port
}
