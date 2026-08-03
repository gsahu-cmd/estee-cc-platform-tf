output "api_key_id" {
  value     = confluent_api_key.apikey.id
  sensitive = true
}

output "api_key_secret" {
  value     = confluent_api_key.apikey.secret
  sensitive = true
}

output "owner_service_account_id" {
  value = var.elc_mod_service_account_id
}
