variable "elc_mod_environment_id" {
  description = "Confluent environment ID"
  type        = string
}

variable "elc_mod_gateway_id" {
  description = "Confluent gateway ID"
  type        = string
}

variable "elc_mod_private_endpoints" {
  description = "Map of Azure private endpoints to register as Confluent access points"
  type = map(object({
    elc_mod_display_name                 = string
    elc_mod_private_endpoint_resource_id = string
  }))

  validation {
    condition     = length(var.elc_mod_private_endpoints) >= 1 && length(var.elc_mod_private_endpoints) <= 3
    error_message = "Provide between 1 and 3 Azure private endpoints."
  }
}
