output "identity_pool_ids" {
  description = "Identity pool IDs by key"
  value       = module.identity_pool.identity_pool_ids
}

output "identity_pool_names" {
  description = "Identity pool names by key"
  value       = module.identity_pool.identity_pool_names
}
