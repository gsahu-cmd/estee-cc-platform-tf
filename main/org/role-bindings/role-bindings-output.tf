output "role_binding_ids" {
  description = "Role binding IDs by key"
  value       = module.cc_role_bindings.identity_pool_role_binding_ids
}
