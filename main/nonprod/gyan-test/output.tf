output "environment_id" {
  description = "The ID of the Confluent environment."
  value       = module.gyan-test-eastus2-cc-env.environment_id
}

output "environment_name" {
  description = "The name of the Confluent environment."
  value       = module.gyan-test-eastus2-cc-env.environment_display_name
}

/*
output "gateway_id" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.ingress_gateway_id
}

output "private_link_service_alias" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.azure_ingress_private_link_gateway[0].private_link_service_alias
}

output "private_link_service_resource_id" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.azure_ingress_private_link_gateway[0].private_link_service_resource_id
}
*/

output "gateway_id" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.gateway_id
}

output "private_link_service_alias" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.private_link_service_alias
}

output "private_link_service_resource_id" {
  value = module.gyan-test-eastus2-cc-ingress-gateway.private_link_service_resource_id
}
