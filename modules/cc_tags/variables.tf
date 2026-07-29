variable "elc_mod_tags" {
  description = "Map of Confluent tags to create. Key is tag name, value is tag description"
  type        = map(string)
  
  validation {
    condition     = length(var.elc_mod_tags) > 0
    error_message = "At least one tag must be provided."
  }
}
