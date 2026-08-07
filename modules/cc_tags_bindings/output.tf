output "topic_tag_binding_ids" {
	description = "Tag binding IDs keyed by topic name and tag name."
	value = {
		for key, binding in confluent_tag_binding.topic_tag : key => binding.id
	}
}
