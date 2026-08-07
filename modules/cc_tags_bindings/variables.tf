variable "elc_mod_topic_tag_bindings" {
	description = "List of tag bindings to apply to Kafka topics. Each item creates one tag binding."
	type = list(object({
		topic_name             = string
		tag_name               = string
		disable_wait_for_ready = optional(bool, false)
	}))

	validation {
		condition = alltrue([
			for binding in var.elc_mod_topic_tag_bindings :
			length(trimspace(binding.topic_name)) > 0 && length(trimspace(binding.tag_name)) > 0
		])
		error_message = "topic_name and tag_name must not be empty."
	}
}

variable "elc_mod_schema_registry_id" {
	description = "Schema Registry cluster ID used in Kafka topic qualified names."
	type        = string
}

variable "elc_mod_kafka_cluster_id" {
	description = "Kafka cluster ID used in Kafka topic qualified names."
	type        = string
}
