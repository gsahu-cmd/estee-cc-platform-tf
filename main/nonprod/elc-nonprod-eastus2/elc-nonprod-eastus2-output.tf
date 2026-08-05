output "environment_id" {
  description = "The ID of the Confluent environment."
  value       = module.elc-nonprod-eastus2-cc-env.environment_id
}

output "environment_name" {
  description = "The name of the Confluent environment."
  value       = module.elc-nonprod-eastus2-cc-env.environment_display_name
}

output "cluster_id" {
  description = "The ID of the Confluent Kafka cluster."
  value       = module.elc-nonprod-eastus2-cc-cluster-enterprise.cluster_id
}

output "cluster_name" {
  description = "The name of the Confluent Kafka cluster."
  value       = module.elc-nonprod-eastus2-cc-cluster-enterprise.cluster_name
}

output "bootstrap_endpoint" {
  description = "The bootstrap servers for the Confluent Kafka cluster."
  value       = module.elc-nonprod-eastus2-cc-cluster-enterprise.bootstrap_endpoint
}