variable "elc_mod_group_mappings" {
  description = "Map of SSO group mappings to create"
  type = map(object({
    display_name = string
    description  = optional(string)
    filter       = string
  }))
}