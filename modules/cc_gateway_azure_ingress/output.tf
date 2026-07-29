output "gateway_id" {
  description = "Confluent Gateway ID"
  value       = confluent_gateway.gateway.id
}

output "gateway_name" {
  description = "Confluent Gateway display name"
  value       = confluent_gateway.gateway.display_name
}

output "gateway_address" {
  description = "Gateway address for connectivity"
  value       = confluent_gateway.gateway.gateway_address
}