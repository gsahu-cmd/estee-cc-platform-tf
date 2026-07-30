output "service_account_ids" {
  description = "Map of created service account IDs"
  value       = module.service_account_sa.service_account_ids
}

output "service_account_display_names" {
  description = "Map of created service account display names"
  value       = module.service_account_sa.service_account_names
}
