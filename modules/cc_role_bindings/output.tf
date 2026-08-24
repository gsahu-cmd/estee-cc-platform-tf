output "role_binding_ids" {
  description = "Role binding IDs by key"
  value = {
    for k, v in confluent_role_binding.pool_binding : k => v.id
  }
}

output "identity_pool_role_binding_ids" {
  description = "Role binding IDs by key"
  value = {
    for k, v in confluent_role_binding.pool_binding : k => v.id
  }
}
