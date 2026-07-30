resource "confluent_identity_provider" "oidc" {
  display_name = var.elc_mod_oidc_display_name
  description  = var.elc_mod_oidc_description
  issuer       = var.elc_mod_oidc_issuer_uri
  jwks_uri     = var.elc_mod_oidc_jwks_uri

  # Optional. If null, omit it and let provider default apply.
  #identity_claim = var.elc_mod_oidc_identity_claim
}
