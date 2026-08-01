output "topic_ids" {
  description = "Kafka topic IDs created by the topic module."
  value       = module.cc_topic_creation.topic_ids
}

output "topic_names" {
  description = "Kafka topic names created by the topic module."
  value       = module.cc_topic_creation.topic_names
}