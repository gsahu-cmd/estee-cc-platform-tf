variable "elc_mod_environment_id" {
  description = "Confluent environment ID"
  type        = string
}

variable "elc_mod_cluster_name" {
  description = "Kafka cluster name"
  type        = string
}

variable "elc_mod_cluster_cloud" {
  description = "Cloud provider (AWS, AZURE, or GCP)"
  type        = string
}

variable "elc_mod_cluster_region" {
  description = "Confluent Cloud region for Azure"
  type        = string
}

variable "elc_mod_cluster_availability" {
  description = "Dedicated cluster availability: SINGLE_ZONE or MULTI_ZONE"
  type        = string

  validation {
    condition     = contains(["SINGLE_ZONE", "MULTI_ZONE"], var.elc_mod_cluster_availability)
    error_message = "elc_mod_cluster_availability must be SINGLE_ZONE or MULTI_ZONE."
  }
}

variable "elc_mod_cluster_cku" {
  description = "Number of CKUs for the Dedicated cluster"
  type        = number
}

# Use only if private networking is required
# variable "elc_mod_network_id" {
#   description = "Confluent Cloud network ID for private networking"
#   type        = string
# }
