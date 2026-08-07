module "identity_pool_nonprod" {
  source = "../../../../modules/cc_identity_pool"

  elc_mod_oidc_identity_provider_id = data.confluent_identity_provider.pingone.id
  elc_mod_oidc_identity_pools       = jsondecode(file("${path.module}/ip-nonprod.json"))
}