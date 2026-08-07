variable "elc_mod_kafka_acls" {
  description = "Kafka ACLs to create in the provider-configured Confluent Kafka cluster."
  type = map(object({
    resource_type = string
    resource_name = string
    pattern_type  = string
    principal     = string
    host          = optional(string, "*")
    operation     = string
    permission    = string
  }))

  validation {
    condition = alltrue([
      for acl in var.elc_mod_kafka_acls :
      contains(["TOPIC", "GROUP", "CLUSTER", "TRANSACTIONAL_ID", "DELEGATION_TOKEN"], acl.resource_type)
    ])
    error_message = "resource_type must be one of TOPIC, GROUP, CLUSTER, TRANSACTIONAL_ID, or DELEGATION_TOKEN."
  }

  validation {
    condition = alltrue([
      for acl in var.elc_mod_kafka_acls :
      contains(["LITERAL", "PREFIXED"], acl.pattern_type)
    ])
    error_message = "pattern_type must be LITERAL or PREFIXED."
  }

  validation {
    condition = alltrue([
      for acl in var.elc_mod_kafka_acls :
      contains(["ALL", "READ", "WRITE", "CREATE", "DELETE", "ALTER", "DESCRIBE", "CLUSTER_ACTION", "DESCRIBE_CONFIGS", "ALTER_CONFIGS", "IDEMPOTENT_WRITE"], acl.operation)
    ])
    error_message = "operation must be a valid Kafka ACL operation."
  }

  validation {
    condition = alltrue([
      for acl in var.elc_mod_kafka_acls :
      contains(["ALLOW", "DENY"], acl.permission)
    ])
    error_message = "permission must be ALLOW or DENY."
  }

  validation {
    condition = alltrue([
      for acl in var.elc_mod_kafka_acls :
      length(trimspace(acl.resource_name)) > 0 &&
      length(trimspace(acl.principal)) > 0 &&
      length(trimspace(acl.host)) > 0
    ])
    error_message = "resource_name, principal, and host must not be empty."
  }

  validation {
    condition = alltrue([
      for acl in var.elc_mod_kafka_acls :
      acl.resource_type != "CLUSTER" || acl.resource_name == "kafka-cluster"
    ])
    error_message = "resource_name must be kafka-cluster when resource_type is CLUSTER."
  }
}