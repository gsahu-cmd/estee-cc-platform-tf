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

variable "environment_id" {
  description = "Confluent Cloud environment ID"
  type        = string
}

variable "kafka_cluster_id" {
  description = "Confluent Kafka cluster ID"
  type        = string
}

variable "kafka_rest_endpoint" {
  description = "Kafka REST endpoint for this cluster. Use public endpoint locally and private endpoint from Azure DevOps."
  type        = string
}

variable "kafka_api_key" {
  description = "Kafka API key for this cluster"
  type        = string
  sensitive   = true
}

variable "kafka_api_secret" {
  description = "Kafka API secret for this cluster"
  type        = string
  sensitive   = true
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
