output "environment_id" {
  description = "The ID of the Confluent environment."
  value       = module.elc-nonprod-southeastasia-cc-env.environment_id
}

output "environment_name" {
  description = "The name of the Confluent environment."
  value       = module.elc-nonprod-southeastasia-cc-env.environment_display_name
}