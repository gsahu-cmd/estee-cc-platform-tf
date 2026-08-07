resource "confluent_catalog_entity_attributes" "topic" {
	for_each = var.elc_mod_topic_catalog_attributes

	entity_name = "${var.elc_mod_kafka_cluster_id}:${each.key}"
	entity_type = "kafka_topic"
	attributes = {
		owner       = each.value.owner
		ownerEmail  = each.value.ownerEmail
		description = each.value.description
	}

	lifecycle {
		prevent_destroy = true
	}
}