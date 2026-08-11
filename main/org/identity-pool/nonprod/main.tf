locals {
  elc_identity_pools_file = "${path.module}/files/elc-identity-pools.json"
  elc_identity_pools      = fileexists(local.elc_identity_pools_file) ? jsondecode(file(local.elc_identity_pools_file)) : {}
}

module "identity_pool_nonprod" {
  source = "../../../../modules/cc_identity_pool"

  elc_mod_oidc_identity_provider_id = data.confluent_identity_provider.pingone.id
  elc_mod_oidc_identity_pools       = local.elc_identity_pools
}