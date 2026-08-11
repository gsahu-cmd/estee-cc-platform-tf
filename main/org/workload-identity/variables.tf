variable "confluent_cloud_api_key" {
  description = "Bootstrap Cloud API key with OrganizationAdmin"
  type        = string
  sensitive   = true
}

variable "confluent_cloud_api_secret" {
  description = "Bootstrap Cloud API secret with OrganizationAdmin"
  type        = string
  sensitive   = true
}

variable "elc_oidc_display_name" {
  description = "Display name for the Confluent OAuth/OIDC identity provider"
  type        = string
}

variable "elc_oidc_description" {
  description = "Description for the Confluent OAuth/OIDC identity provider"
  type        = string
}

variable "elc_oidc_issuer_uri" {
  description = "Issuer URI for the external OIDC provider"
  type        = string
}

variable "elc_oidc_jwks_uri" {
  description = "JWKS URI for the external OIDC provider"
  type        = string
}

/*
variable "elc_mod_oidc_identity_claim" {
  description = "Claim used to identify the external identity in audit logs"
  type        = string
  default     = "claims.sub"
}
*/