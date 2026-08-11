output "identity_pool_ids" {
  description = "Prod identity pool IDs by key"
  value       = module.identity_pool_prod.identity_pool_ids
}

output "identity_pool_names" {
  description = "Prod identity pool names by key"
  value       = module.identity_pool_prod.identity_pool_names
}