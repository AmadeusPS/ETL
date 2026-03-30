output "api_url" {
  description = "Container App FQDN for the backend API"
  value       = "https://${azurerm_container_app.api.latest_revision_fqdn}"
}

output "acr_api_image" {
  description = "ACR image path for the API (tag with :latest or git SHA)"
  value       = "${azurerm_container_registry.main.login_server}/${var.project}/api"
}

output "acr_worker_image" {
  description = "ACR image path for the Celery worker"
  value       = "${azurerm_container_registry.main.login_server}/${var.project}/worker"
}

output "key_vault_uri" {
  description = "Azure Key Vault URI"
  value       = azurerm_key_vault.main.vault_uri
}

output "resource_group_name" {
  description = "Azure Resource Group name"
  value       = azurerm_resource_group.main.name
}
