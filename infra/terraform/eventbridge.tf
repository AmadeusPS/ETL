# ---------------------------------------------------------------------------
# Azure Functions – Timer Trigger for scraping 2x/day
# (replaces AWS EventBridge cron + Lambda)
# ---------------------------------------------------------------------------

resource "azurerm_storage_account" "functions" {
  name                     = "${replace(var.project, "-", "")}${var.environment}func"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = { Project = var.project, Environment = var.environment }
}

resource "azurerm_service_plan" "functions" {
  name                = "${var.project}-${var.environment}-func-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "Y1"  # Consumption (serverless) plan
}

resource "azurerm_linux_function_app" "scrape_trigger" {
  name                       = "${var.project}-${var.environment}-scrape"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  storage_account_name       = azurerm_storage_account.functions.name
  storage_account_access_key = azurerm_storage_account.functions.primary_access_key
  service_plan_id            = azurerm_service_plan.functions.id

  site_config {
    application_stack {
      python_version = "3.12"
    }
    vnet_route_all_enabled = true
  }

  app_settings = {
    REDIS_URL                      = "rediss://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:${azurerm_redis_cache.main.ssl_port}/0"
    FUNCTIONS_WORKER_RUNTIME       = "python"
    AzureWebJobsFeatureFlags       = "EnableWorkerIndexing"
    SCM_DO_BUILD_DURING_DEPLOYMENT = "true"
  }

  virtual_network_subnet_id = azurerm_subnet.functions.id

  tags = { Project = var.project, Environment = var.environment }
}
