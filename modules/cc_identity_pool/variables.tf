variable "elc_mod_oidc_identity_provider_id" {
  description = "Confluent identity provider ID"
  type        = string
}

variable "elc_mod_oidc_identity_pools" {
  description = "Map of identity pools to create"
  type = map(object({
    display_name   = string
    description    = string
    identity_claim = string
    filter         = string
  }))

  validation {
    condition     = length(var.elc_mod_oidc_identity_pools) >= 1
    error_message = "At least one identity pool must be provided."
  }
}
