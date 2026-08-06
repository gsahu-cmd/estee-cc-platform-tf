output "environment_id" {
  description = "The ID of the Confluent environment."
  value       = module.gyan-test-eastus2-cc-env.environment_id
}

output "environment_name" {
  description = "The name of the Confluent environment."
  value       = module.gyan-test-eastus2-cc-env.environment_display_name
}

output "gateway_id" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.gateway_id
}

output "private_link_service_alias" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.private_link_service_alias
}

output "private_link_service_resource_id" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.private_link_service_resource_id
}

/*
output "access_point_ids" {
  description = "Confluent access point IDs by key."
  value       = module.gyan-test-eastus2-cc-access-point.access_point_ids
}

output "access_point_names" {
  description = "Confluent access point names by key."
  value       = module.gyan-test-eastus2-cc-access-point.access_point_names
}

output "access_point_private_endpoint_resource_ids" {
  description = "Azure private endpoint resource IDs by key."
  value       = module.gyan-test-eastus2-cc-access-point.access_point_private_endpoint_resource_ids
}

output "access_point_dns_domains" {
  description = "DNS domains by access point."
  value       = module.gyan-test-eastus2-cc-access-point.access_point_dns_domains
}

output "access_point_private_link_service_aliases" {
  description = "Private Link service aliases by access point."
  value       = module.gyan-test-eastus2-cc-access-point.access_point_private_link_service_aliases
}

output "access_point_private_link_service_resource_ids" {
  description = "Private Link service resource IDs by access point."
  value       = module.gyan-test-eastus2-cc-access-point.access_point_private_link_service_resource_ids
}
*/
