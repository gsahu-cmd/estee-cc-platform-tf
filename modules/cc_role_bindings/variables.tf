variable "elc_mod_role_bindings" {
  description = "Map of role bindings for identity pools or SSO group mappings"
  type = map(object({
    identity_pool_id         = optional(string)
    group_mapping_id         = optional(string)
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
      for _, v in var.elc_mod_role_bindings :
      (v.identity_pool_id != null) != (v.group_mapping_id != null)
    ])
    error_message = "Exactly one of identity_pool_id or group_mapping_id must be provided."
  }

  validation {
    condition = alltrue([
      for _, v in var.elc_mod_role_bindings :
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
