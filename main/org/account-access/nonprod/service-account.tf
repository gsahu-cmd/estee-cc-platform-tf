module "service_account_sa" {
  source = "../../../../modules/cc_service_accounts"

  elc_mod_service_accounts = local.elc_service_accounts
}