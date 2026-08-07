output "identity_pool_ids" {
  description = "Nonprod identity pool IDs by key"
  value       = module.identity_pool_nonprod.identity_pool_ids
}

output "identity_pool_names" {
  description = "Nonprod identity pool names by key"
  value       = module.identity_pool_nonprod.identity_pool_names
}