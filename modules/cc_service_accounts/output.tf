output "service_account_ids" {
  description = "Service account IDs by key"
  value = {
    for k, v in confluent_service_account.service_account : k => v.id
  }
}

output "service_account_names" {
  description = "Service account display names by key"
  value = {
    for k, v in confluent_service_account.service_account : k => v.display_name
  }
}

output "service_account_api_versions" {
  description = "Service account API versions by key"
  value = {
    for k, v in confluent_service_account.service_account : k => v.api_version
  }
}

output "service_account_kinds" {
  description = "Service account kinds by key"
  value = {
    for k, v in confluent_service_account.service_account : k => v.kind
  }
}
