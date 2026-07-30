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

variable "elc_cluster_name" {
  description = "Confluent Kafka cluster name"
  type        = string
}

variable "elc_cluster_cloud" {
  description = "Cloud provider (AWS, AZURE, or GCP)"
  type        = string
}

variable "elc_cluster_region" {
  description = "Confluent Cloud region"
  type        = string
}

variable "elc_cluster_availability" {
  description = "Cluster availability - LOW/SINGLE_ZONE or HIGH/MULTI_ZONE"
  type        = string
}

variable "schema_registry_id" {
  description = "Schema Registry ID"
  type        = string
}

variable "catalog_rest_endpoint" {
  description = "Catalog REST endpoint"
  type        = string
}

variable "schema_registry_api_key" {
  description = "Schema Registry API key"
  type        = string
  sensitive   = true
}

variable "schema_registry_api_secret" {
  description = "Schema Registry API secret"
  type        = string
  sensitive   = true
}

variable "elc_tags" {
  description = "Map of Confluent tags to create. Key is tag name, value is tag description"
  type        = map(string)
}

variable "elc_gateway_name" {
  type = string
}

/*
variable "elc_cluster_max_ecku" {
  description = "Maximum number of eCKUs for the Enterprise cluster"
  type        = number
  default = 1
}

variable "elc_network_id" {
  description = "Optional Confluent network ID for private networking"
  type        = string
}

variable "elc_private_endpoints" {
  description = "Optional map of private endpoints for the cluster"
  type        = map(object({
    display_name                 = string
    private_endpoint_resource_id = string
  }))
}
*/
