module "api_key" {
  source = "../../../modules/cc_api_key"

  elc_mod_display_name       = "estee-org-api-key"
  elc_mod_description        = "Global API key for org-level use"
  elc_mod_service_account_id = var.elc_service_account_id
}
