output "cluster_id" {
  description = "The ID of the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.basic.id
}

output "cluster_name" {
  description = "The name of the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.basic.display_name
}

output "bootstrap_endpoint" {
  description = "The bootstrap servers for the Confluent Kafka cluster."
  value       = confluent_kafka_cluster.basic.bootstrap_endpoint
}
