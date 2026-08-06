output "gateway_id" {
  description = "Confluent Gateway ID"
  value       = confluent_gateway.gateway.id
}

output "gateway_name" {
  description = "Confluent Gateway display name"
  value       = confluent_gateway.gateway.display_name
}

output "private_link_service_alias" {
  description = "Azure Private Link Service alias"
  value       = confluent_gateway.gateway.azure_ingress_private_link_gateway[0].private_link_service_alias
}

output "private_link_service_resource_id" {
  description = "Azure Private Link Service resource ID"
  value       = confluent_gateway.gateway.azure_ingress_private_link_gateway[0].private_link_service_resource_id
}
