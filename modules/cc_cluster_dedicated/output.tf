output "cluster_id" {
  description = "The ID of the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.dedicated.id
}

output "cluster_name" {
  description = "The name of the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.dedicated.display_name
}

output "bootstrap_endpoint" {
  description = "The bootstrap endpoint of the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.dedicated.bootstrap_endpoint
}

output "rest_endpoint" {
  description = "The REST endpoint of the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.dedicated.rest_endpoint
}

output "api_version" {
  description = "The API version of the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.dedicated.api_version
}
