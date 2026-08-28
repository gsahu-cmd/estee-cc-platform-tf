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