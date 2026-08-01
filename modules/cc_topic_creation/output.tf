output "topic_ids" {
	description = "Kafka topic IDs keyed by topic name."
	value       = { for topic_name, topic in confluent_kafka_topic.main : topic_name => topic.id }
}

output "topic_names" {
	description = "Kafka topic names created by this module."
	value       = { for topic_name, topic in confluent_kafka_topic.main : topic_name => topic.topic_name }
}

output "topics" {
	description = "Kafka topic resources created by this module, keyed by topic name."
	value       = confluent_kafka_topic.main
}