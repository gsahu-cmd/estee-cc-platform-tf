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