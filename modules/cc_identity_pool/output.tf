output "identity_pool_ids" {
  description = "Identity pool IDs by key"
  value = {
    for k, v in confluent_identity_pool.pool : k => v.id
  }
}

output "identity_pool_names" {
  description = "Identity pool names by key"
  value = {
    for k, v in confluent_identity_pool.pool : k => v.display_name
  }
}
