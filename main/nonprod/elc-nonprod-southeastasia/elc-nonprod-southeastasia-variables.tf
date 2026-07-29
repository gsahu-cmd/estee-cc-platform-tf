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

/*
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


variable "elc_cluster_max_ecku" {
  description = "Maximum number of eCKUs for the Enterprise cluster"
  type        = number
  default = 1
}

variable "elc_network_id" {
  description = "Optional Confluent network ID for private networking"
  type        = string
}
*/
