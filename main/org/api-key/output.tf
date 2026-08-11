output "api_key_id" {
  value     = module.api_key.api_key_id
  sensitive = true
}

output "api_key_secret" {
  value     = module.api_key.api_key_secret
  sensitive = true
}

output "owner_service_account_id" {
  value = var.elc_service_account_id
}
