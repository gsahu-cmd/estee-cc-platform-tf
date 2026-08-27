output "identity_pool_ids" {
  description = "Nonprod identity pool IDs by key"
  value       = module.identity_pool_nonprod.identity_pool_ids
}

output "identity_pool_names" {
  description = "Nonprod identity pool names by key"
  value       = module.identity_pool_nonprod.identity_pool_names
}

output "group_mapping_ids" {
  description = "Nonprod group mapping IDs by key"
  value       = module.group_mapping_nonprod.group_mapping_ids
}

output "group_mapping_names" {
  description = "Nonprod group mapping names by key"
  value       = module.group_mapping_nonprod.group_mapping_names
}

output "service_account_ids" {
  description = "Map of created service account IDs"
  value       = module.service_account_sa.service_account_ids
}

output "service_account_display_names" {
  description = "Map of created service account display names"
  value       = module.service_account_sa.service_account_names
}

output "identity_provider_id" {
  description = "Confluent identity provider ID"
  value       = module.workload_identity.identity_provider_id
}

output "identity_provider_name" {
  description = "Confluent identity provider display name"
  value       = module.workload_identity.identity_provider_name
}
