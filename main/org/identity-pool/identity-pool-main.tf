module "identity_pool" {
  source = "../../../modules/cc_identity_pool"

  elc_mod_oidc_identity_provider_id = var.elc_oidc_identity_provider_id
  elc_mod_oidc_identity_pools       = var.elc_oidc_identity_pools
}

