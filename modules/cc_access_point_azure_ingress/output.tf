output "access_point_id" {
  description = "Confluent Access Point ID"
  value       = confluent_access_point.access_point.id
}

output "access_point_name" {
  description = "Confluent Access Point display name"
  value       = confluent_access_point.access_point.display_name
}

output "access_point_address" {
  description = "Access Point address for client connections"
  value       = confluent_access_point.access_point.api_endpoint
}