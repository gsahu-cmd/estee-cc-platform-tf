variable "elc_mod_topic_catalog_attributes" {
	description = "Built-in Stream Catalog attributes to apply to Kafka topics."
	type = map(object({
		owner       = optional(string, "")
		ownerEmail  = optional(string, "")
		description = optional(string, "")
	}))

	validation {
		condition = alltrue([
			for topic_name, attributes in var.elc_mod_topic_catalog_attributes :
			length(trimspace(topic_name)) > 0
		])
		error_message = "Topic catalog attribute keys must be non-empty topic names."
	}
}

variable "elc_mod_kafka_cluster_id" {
	description = "Kafka cluster ID used in Kafka topic qualified names."
	type        = string
}