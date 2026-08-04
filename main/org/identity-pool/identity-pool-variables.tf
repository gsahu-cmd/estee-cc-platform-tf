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

variable "elc_oidc_identity_provider_id" {
  description = "Confluent identity provider ID"
  type        = string
}

variable "elc_oidc_identity_pools" {
  description = "Map of identity pools to create"
  type = map(object({
    display_name   = string
    description    = string
    identity_claim = string
    filter         = string
  }))
}