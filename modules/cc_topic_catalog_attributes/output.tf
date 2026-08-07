output "topic_catalog_attribute_ids" {
	description = "Topic catalog attribute IDs keyed by topic name."
	value = {
		for topic_name, attributes in confluent_catalog_entity_attributes.topic : topic_name => attributes.id
	}
}