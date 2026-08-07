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

variable "nonprod_oidc_identity_provider_id" {
  description = "Confluent workload identity provider ID for nonprod"
  type        = string
}