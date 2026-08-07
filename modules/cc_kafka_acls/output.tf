output "kafka_acl_ids" {
  description = "Kafka ACL IDs keyed by ACL map key."
  value = {
    for key, acl in confluent_kafka_acl.acl : key => acl.id
  }
}