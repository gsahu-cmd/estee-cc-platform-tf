variable "elc_mod_access_point_name" {
  description = "Name of the Confluent ingress access point"
  type        = string
}

variable "elc_mod_environment_id" {
  description = "Confluent environment ID"
  type        = string
}

variable "elc_mod_gateway_id" {
  description = "Confluent gateway ID"
  type        = string
}

variable "elc_mod_private_endpoint_resource_id" {
  description = "Azure Private Endpoint resource ID"
  type        = string
}
