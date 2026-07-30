output "identity_provider_id" {
  description = "Confluent identity provider ID"
  value       = confluent_identity_provider.oidc.id
}

output "identity_provider_name" {
  description = "Confluent identity provider display name"
  value       = confluent_identity_provider.oidc.display_name
}
