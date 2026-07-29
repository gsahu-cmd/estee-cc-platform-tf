output "environment_id" {
  description = "The ID of the Confluent environment."
  value       = module.elc-sandbox-cc-env.environment_id
}

output "environment_name" {
  description = "The name of the Confluent environment."
  value       = module.elc-sandbox-cc-env.environment_display_name
}

output "cluster_id" {
  description = "The ID of the Confluent Kafka cluster."
  value       = module.elc-sandbox-cc-cluster.cluster_id
}

output "cluster_name" {
  description = "The name of the Confluent Kafka cluster."
  value       = module.elc-sandbox-cc-cluster.cluster_name
}

output "bootstrap_endpoint" {
  description = "The bootstrap servers for the Confluent Kafka cluster."
  value       = module.elc-sandbox-cc-cluster.bootstrap_endpoint
}

output "tags" {
  description = "The tags created for the Confluent Data Platform resources."
  value       = module.elc_sandbox_tags.tags
}