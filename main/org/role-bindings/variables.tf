variable "confluent_cloud_api_key" {
  description = "Confluent Cloud API key"
  type        = string
  sensitive   = true
}

variable "confluent_cloud_api_secret" {
  description = "Confluent Cloud API secret"
  type        = string
  sensitive   = true
}

variable "elc_identity_pool_role_bindings" {
  description = "Map of org-level role bindings for identity pools"
  type = map(object({
    identity_pool_id       = string
    role_name              = string
    resource_kind          = string
    resource_name          = optional(string)
    kafka_cluster_id       = optional(string)
    kafka_cluster_rbac_crn = optional(string)
    environment_crn        = optional(string)
    organization_crn       = optional(string)
    crn_pattern_override   = optional(string)
    disable_wait_for_ready = optional(bool, false)
  }))

  validation {
    condition     = length(var.elc_root_org_role_bindings) >= 1
    error_message = "At least one role binding must be provided."
  }

  validation {
    condition = alltrue([
      for _, v in var.elc_root_org_role_bindings :
      contains([
        "organization",
        "environment",
        "kafka_cluster",
        "topic",
        "consumer_group",
        "transactional_id",
        "connector",
        "service_account"
      ], v.resource_kind)
    ])
    error_message = "resource_kind must be one of: organization, environment, kafka_cluster, topic, consumer_group, transactional_id, connector, service_account."
  }
}
