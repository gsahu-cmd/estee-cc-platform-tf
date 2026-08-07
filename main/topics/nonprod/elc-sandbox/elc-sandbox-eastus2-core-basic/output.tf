output "topic_ids" {
  description = "Kafka topic IDs created by the topic module."
  value       = module.topic_creation.topic_ids
}

output "topic_names" {
  description = "Kafka topic names created by the topic module."
  value       = module.topic_creation.topic_names
}

output "role_binding_ids" {
  description = "Role binding IDs by key"
  value       = module.cc_role_bindings.identity_pool_role_binding_ids
}

output "kafka_acl_ids" {
  description = "Kafka ACL IDs by key"
  value       = module.cc_kafka_acls.kafka_acl_ids
}

output "topic_tag_binding_ids" {
  description = "Topic tag binding IDs by topic name and tag name"
  value       = module.cc_tags_bindings.topic_tag_binding_ids
}

output "topic_catalog_attribute_ids" {
  description = "Topic catalog attribute IDs by topic name"
  value       = module.cc_topic_catalog_attributes.topic_catalog_attribute_ids
}
