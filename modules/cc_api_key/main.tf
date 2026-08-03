resource "confluent_api_key" "apikey" {
  display_name = var.elc_mod_display_name
  description  = var.elc_mod_description

  owner {
    id          = var.elc_mod_service_account_id
    api_version = "iam/v2"
    kind        = "ServiceAccount"
  }

  managed_resource {
    id          = "global"
    api_version = "global/v1"
    kind        = "Global"
  }
}
