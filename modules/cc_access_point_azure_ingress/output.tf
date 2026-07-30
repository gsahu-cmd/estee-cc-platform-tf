output "access_point_ids" {
  description = "Access Point IDs by key"
  value = {
    for k, v in confluent_access_point.access_point : k => v.id
  }
}

output "access_point_names" {
  description = "Access Point names by key"
  value = {
    for k, v in confluent_access_point.access_point : k => v.display_name
  }
}

output "access_point_private_endpoint_resource_ids" {
  description = "Azure private endpoint resource IDs by key"
  value = {
    for k, v in confluent_access_point.access_point :
    k => v.azure_ingress_private_link_endpoint[0].private_endpoint_resource_id
  }
}

output "access_point_dns_domains" {
  description = "DNS domains by access point"
  value = {
    for k, v in confluent_access_point.access_point :
    k => v.azure_ingress_private_link_endpoint[0].dns_domain
  }
}

output "access_point_private_link_service_aliases" {
  description = "Private Link service aliases by access point"
  value = {
    for k, v in confluent_access_point.access_point :
    k => v.azure_ingress_private_link_endpoint[0].private_link_service_alias
  }
}

output "access_point_private_link_service_resource_ids" {
  description = "Private Link service resource IDs by access point"
  value = {
    for k, v in confluent_access_point.access_point :
    k => v.azure_ingress_private_link_endpoint[0].private_link_service_resource_id
  }
}
