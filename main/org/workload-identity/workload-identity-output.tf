output "identity_provider_id" {
  description = "Confluent identity provider ID"
  value       = module.workload_identity.identity_provider_id
}

output "identity_provider_name" {
  description = "Confluent identity provider display name"
  value       = module.workload_identity.identity_provider_name
}
