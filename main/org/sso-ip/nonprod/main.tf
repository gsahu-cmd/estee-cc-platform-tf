locals {
  elc_identity_pools_file   = "${path.module}/files/elc-identity-pools.json"
  elc_group_mappings_file   = "${path.module}/files/elc-group-mappings.json"
  elc_identity_pools        = fileexists(local.elc_identity_pools_file) ? jsondecode(file(local.elc_identity_pools_file)) : {}
  elc_group_mappings        = fileexists(local.elc_group_mappings_file) ? jsondecode(file(local.elc_group_mappings_file)) : {}
  elc_service_accounts = {
    for account_key, account in var.elc_service_accounts : "${trimsuffix(account_key, "-${var.platform_environment}")}-${var.platform_environment}" => {
      elc_mod_sa_display_name = "${trimsuffix(account.elc_sa_display_name, "-${var.platform_environment}")}-${var.platform_environment}"
      elc_mod_sa_description  = account.elc_sa_description
    }
  }
}

module "identity_pool_nonprod" {
  source = "../../../../modules/cc_identity_pool"

  elc_mod_oidc_identity_provider_id = module.workload_identity.identity_provider_id
  elc_mod_oidc_identity_pools       = local.elc_identity_pools
}

module "group_mapping_nonprod" {
  source = "../../../../modules/cc_group_mapping"

  elc_mod_group_mappings = local.elc_group_mappings
}