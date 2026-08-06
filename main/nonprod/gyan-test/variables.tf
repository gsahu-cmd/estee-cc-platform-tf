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

variable "elc_env_name" {
  description = "Confluent environment name"
  type        = string
}

variable "elc_env_stream_package" {
  description = "Confluent environment Stream package name "
  type        = string
}

variable "elc_cluster_region" {
  description = "Confluent Cloud region"
  type        = string
}

variable "elc_ingress_gateway_name" {
  description = "Confluent ingress gateway name"
  type        = string  
}
