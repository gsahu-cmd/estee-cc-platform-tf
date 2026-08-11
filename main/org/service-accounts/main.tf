module "service_account_sa" {
  source = "../../../modules/cc_service_accounts"

  elc_mod_service_accounts = {
    for k, v in var.elc_service_accounts : k => {
      elc_mod_sa_display_name = v.elc_sa_display_name
      elc_mod_sa_description  = v.elc_sa_description
    }
  }
}
