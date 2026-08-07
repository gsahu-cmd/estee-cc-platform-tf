resource "confluent_tag_binding" "topic_tag" {
	for_each = {
		for binding in var.elc_mod_topic_tag_bindings :
		"${binding.topic_name}.${binding.tag_name}" => binding
	}

	tag_name               = each.value.tag_name
	entity_name            = "${var.elc_mod_schema_registry_id}:${var.elc_mod_kafka_cluster_id}:${each.value.topic_name}"
	entity_type            = "kafka_topic"
	disable_wait_for_ready = each.value.disable_wait_for_ready

	lifecycle {
		prevent_destroy = true
	}
}
