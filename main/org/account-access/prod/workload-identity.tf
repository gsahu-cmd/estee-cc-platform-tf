module "workload_identity" {
  source = "../../../../modules/cc_identity_provider"

  elc_mod_oidc_display_name = var.elc_oidc_display_name
  elc_mod_oidc_description  = var.elc_oidc_description
  elc_mod_oidc_issuer_uri   = var.elc_oidc_issuer_uri
  elc_mod_oidc_jwks_uri     = var.elc_oidc_jwks_uri
}