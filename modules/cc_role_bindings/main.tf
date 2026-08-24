resource "confluent_role_binding" "pool_binding" {
  for_each = var.elc_mod_role_bindings

  principal = "User:${coalesce(each.value.identity_pool_id, each.value.group_mapping_id)}"
  role_name = each.value.role_name

  crn_pattern = (
    each.value.crn_pattern_override != null ? each.value.crn_pattern_override :

    each.value.resource_kind == "organization" ? each.value.organization_crn :

    each.value.resource_kind == "environment" ? each.value.environment_crn :

    each.value.resource_kind == "kafka_cluster" ? each.value.kafka_cluster_rbac_crn :

    each.value.resource_kind == "schema_registry" ? each.value.schema_registry_crn :

    each.value.resource_kind == "topic" ? (
      each.value.resource_name_prefix != null ?
      "${each.value.kafka_cluster_rbac_crn}/kafka=${each.value.kafka_cluster_id}/topic=${each.value.resource_name_prefix}*" :
      "${each.value.kafka_cluster_rbac_crn}/kafka=${each.value.kafka_cluster_id}/topic=${each.value.resource_name}"
    ) :

    each.value.resource_kind == "consumer_group" ? (
      "${each.value.kafka_cluster_rbac_crn}/kafka=${each.value.kafka_cluster_id}/group=${each.value.resource_name}"
    ) :

    each.value.resource_kind == "transactional_id" ? (
      "${each.value.kafka_cluster_rbac_crn}/kafka=${each.value.kafka_cluster_id}/transactional-id=${each.value.resource_name}"
    ) :

    each.value.resource_kind == "connector" ? (
      "${each.value.kafka_cluster_rbac_crn}/connector=${each.value.resource_name}"
    ) :

    each.value.resource_kind == "service_account" ? (
      "${each.value.organization_crn}/service-account=${each.value.resource_name}"
    ) :

    null
  )

  disable_wait_for_ready = each.value.disable_wait_for_ready

  lifecycle {
    prevent_destroy = true
  }
}
