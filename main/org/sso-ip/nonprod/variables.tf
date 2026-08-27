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