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
  description = "Confluent Cloud region"
  type        = string
}

variable "elc_mod_cluster_availability" {
  description = "Cluster availability - SINGLE_ZONE or MULTI_ZONE"
  type        = string
}