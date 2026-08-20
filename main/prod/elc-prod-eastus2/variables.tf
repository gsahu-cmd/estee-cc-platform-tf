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

variable "elc_private_endpoints" {
  description = "Azure private endpoints to register as Confluent ingress access points."

  type = map(object({
    elc_mod_display_name                 = string
    elc_mod_private_endpoint_resource_id = string
  }))

  validation {
    condition     = length(var.elc_private_endpoints) >= 1 && length(var.elc_private_endpoints) <= 3
    error_message = "Provide between 1 and 3 Azure private endpoints."
  }
}

variable "elc_cluster_name" {
  description = "Confluent Kafka cluster name"
  type        = string
}

variable "elc_cluster_cloud" {
  description = "Cloud provider (AWS, AZURE, or GCP)"
  type        = string
}

variable "elc_cluster_availability" {
  description = "Cluster availability - SINGLE_ZONE or MULTI_ZONE"
  type        = string
}
