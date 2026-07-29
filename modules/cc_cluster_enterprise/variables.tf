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

  validation {
    condition     = contains(["AWS", "AZURE", "GCP"], upper(var.elc_mod_cluster_cloud))
    error_message = "elc_mod_cluster_cloud must be AWS, AZURE, or GCP."
  }
}

variable "elc_mod_cluster_region" {
  description = "Confluent Cloud region"
  type        = string
}

variable "elc_mod_cluster_availability" {
  description = "Cluster availability. Use LOW/HIGH for newer orgs, or SINGLE_ZONE/MULTI_ZONE for legacy orgs."
  type        = string

  validation {
    condition = contains(
      ["LOW", "HIGH", "SINGLE_ZONE", "MULTI_ZONE"],
      upper(replace(var.elc_mod_cluster_availability, "-", "_"))
    )
    error_message = "elc_mod_cluster_availability must be LOW, HIGH, SINGLE_ZONE, or MULTI_ZONE."
  }
}

variable "elc_mod_cluster_max_ecku" {
  description = "Maximum number of eCKUs for the Enterprise cluster"
  type        = number
  default = 1
  validation {
    condition     = var.elc_mod_cluster_max_ecku >= 1
    error_message = "elc_mod_cluster_max_ecku must be at least 1."
  }
}

variable "elc_mod_network_id" {
  description = "Optional Confluent network ID for private networking"
  type        = string
  default     = null
}
