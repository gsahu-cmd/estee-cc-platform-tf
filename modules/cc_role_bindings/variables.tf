variable "elc_mod_identity_pool_role_bindings" {
  description = "Map of role bindings for identity pools"
  type = map(object({
    identity_pool_id         = string
    role_name                = string
    resource_kind            = string
    resource_name            = optional(string)
    resource_name_prefix     = optional(string)
    kafka_cluster_id         = optional(string)
    kafka_cluster_rbac_crn   = optional(string)
    schema_registry_crn      = optional(string)
    environment_crn          = optional(string)
    organization_crn         = optional(string)
    crn_pattern_override     = optional(string)
    disable_wait_for_ready   = optional(bool, false)
  }))
 
  validation {
    condition = alltrue([
      for _, v in var.elc_mod_identity_pool_role_bindings :
      contains([
        "organization",
        "environment",
        "kafka_cluster",
        "schema_registry",
        "topic",
        "consumer_group",
        "transactional_id",
        "connector",
        "service_account"
      ], v.resource_kind)
    ])
    error_message = "resource_kind must be one of: organization, environment, kafka_cluster, schema_registry, topic, consumer_group, transactional_id, connector, service_account."
  }
}