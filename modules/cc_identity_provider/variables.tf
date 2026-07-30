variable "elc_mod_oidc_display_name" {
  description = "Display name for the Confluent OAuth/OIDC identity provider"
  type        = string
}

variable "elc_mod_oidc_description" {
  description = "Description for the Confluent OAuth/OIDC identity provider"
  type        = string
}

variable "elc_mod_oidc_issuer_uri" {
  description = "Issuer URI for the external OIDC provider"
  type        = string
}

variable "elc_mod_oidc_jwks_uri" {
  description = "JWKS URI for the external OIDC provider"
  type        = string
}

variable "elc_mod_oidc_identity_claim" {
  description = "Claim used to identify the external identity in audit logs"
  type        = string
  default     = "claims.sub"
}
