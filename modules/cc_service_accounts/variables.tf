variable "elc_mod_service_accounts" {
  description = "Map of Confluent service accounts to create"
  type = map(object({
    elc_mod_sa_display_name = string
    elc_mod_sa_description  = string
  }))

  validation {
    condition     = length(var.elc_mod_service_accounts) >= 1
    error_message = "Provide at least one service account."
  }
}
