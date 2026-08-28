data "terraform_remote_state" "account_access" {
  backend = "azurerm"

  config = {
    resource_group_name  = var.account_access_state_resource_group_name
    storage_account_name = var.account_access_state_storage_account_name
    container_name       = var.account_access_state_container_name
    key                  = var.account_access_state_key
  }
}

locals {
  elc_rbac_file               = "${path.module}/files/elc-rbac.json"
  elc_group_mapping_rbac_file = "${path.module}/files/elc-group-mapping-rbac.json"
  elc_rbac_bindings           = fileexists(local.elc_rbac_file) ? jsondecode(file(local.elc_rbac_file)) : {}
  elc_group_mapping_rbac      = fileexists(local.elc_group_mapping_rbac_file) ? jsondecode(file(local.elc_group_mapping_rbac_file)) : {}
  elc_identity_pool_ids       = data.terraform_remote_state.account_access.outputs.identity_pool_ids
  elc_group_mapping_ids       = data.terraform_remote_state.account_access.outputs.group_mapping_ids

  elc_rbac_bindings_with_context = {
    for binding_key, binding in local.elc_rbac_bindings : binding_key => merge(
      {
        kafka_cluster_id       = data.confluent_kafka_cluster.cc_cluster.id
        kafka_cluster_rbac_crn = data.confluent_kafka_cluster.cc_cluster.rbac_crn
        schema_registry_crn    = data.confluent_schema_registry_cluster.cc_schema_registry.resource_name
        environment_crn        = data.confluent_environment.cc_environment.resource_name
        organization_crn       = data.confluent_organization.cc_organization.resource_name
      },
      binding,
      {
        identity_pool_id = try(binding.identity_pool_id, null) != null ? binding.identity_pool_id : local.elc_identity_pool_ids[binding.identity_pool_name]
      }
    )
  }

  elc_group_mapping_rbac_with_context = {
    for binding_key, binding in local.elc_group_mapping_rbac : binding_key => merge(
      {
        kafka_cluster_id       = data.confluent_kafka_cluster.cc_cluster.id
        kafka_cluster_rbac_crn = data.confluent_kafka_cluster.cc_cluster.rbac_crn
        schema_registry_crn    = data.confluent_schema_registry_cluster.cc_schema_registry.resource_name
        environment_crn        = data.confluent_environment.cc_environment.resource_name
        organization_crn       = data.confluent_organization.cc_organization.resource_name
      },
      binding,
      {
        group_mapping_id = try(binding.group_mapping_id, null) != null ? binding.group_mapping_id : local.elc_group_mapping_ids[binding.group_mapping_name]
      }
    )
  }
}

module "cc_role_bindings" {
  source = "../../../../../modules/cc_role_bindings"

  elc_mod_role_bindings = local.elc_rbac_bindings_with_context
}

module "cc_group_mapping_role_bindings" {
  source = "../../../../../modules/cc_role_bindings"

  elc_mod_role_bindings = local.elc_group_mapping_rbac_with_context
}
