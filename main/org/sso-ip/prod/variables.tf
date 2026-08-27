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

variable "oidc_identity_provider_id" {
  description = "Confluent workload identity provider ID"
  type        = string
}


variable "platform_environment" {
  description = "Platform environment suffix used for generated account-access names."
  type        = string

  validation {
    condition     = contains(["nonprod", "prod"], var.platform_environment)
    error_message = "platform_environment must be either nonprod or prod."
  }
}

variable "elc_service_accounts" {
  description = "Map of Confluent service accounts to create"
  type = map(object({
    elc_sa_display_name = string
    elc_sa_description  = string
  }))

  validation {
    condition     = length(var.elc_service_accounts) >= 1
    error_message = "Provide at least one service account."
  }
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
