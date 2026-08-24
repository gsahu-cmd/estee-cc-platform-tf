output "group_mapping_ids" {
  description = "Group mapping IDs by key"
  value = {
    for k, v in confluent_group_mapping.mapping : k => v.id
  }
}

output "group_mapping_names" {
  description = "Group mapping display names by key"
  value = {
    for k, v in confluent_group_mapping.mapping : k => v.display_name
  }
}