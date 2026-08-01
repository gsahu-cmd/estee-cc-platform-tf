resource "confluent_kafka_topic" "main" {
  for_each = var.topics

  topic_name       = each.key
  partitions_count = each.value.partitions_count
  config           = each.value.config

  kafka_cluster {
    id = each.value.cluster_id
  }

  lifecycle {
    prevent_destroy = true
  }
}