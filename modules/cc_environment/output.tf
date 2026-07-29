output "environment_id" {
  description = "Confluent environment ID."
  value       = confluent_environment.elc-environment.id
}

output "environment_display_name" {
  description = "Confluent environment display name."
  value       = confluent_environment.elc-environment.display_name
}
