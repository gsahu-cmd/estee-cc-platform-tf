locals {
  elc_rbac_file     = "${path.module}/files/elc-rbac.json"
  elc_rbac_bindings = fileexists(local.elc_rbac_file) ? jsondecode(file(local.elc_rbac_file)) : {}

  elc_rbac_bindings_with_context = {
    for binding_key, binding in local.elc_rbac_bindings : binding_key => merge(
      {
        kafka_cluster_id       = data.confluent_kafka_cluster.cc_cluster.id
        kafka_cluster_rbac_crn = data.confluent_kafka_cluster.cc_cluster.rbac_crn
        environment_crn        = data.confluent_environment.cc_environment.resource_name
      },
      binding
    )
  }
}

module "cc_role_bindings" {
  source = "../../../../../modules/cc_role_bindings"

  elc_mod_identity_pool_role_bindings = local.elc_rbac_bindings_with_context
  depends_on = [module.topic_creation]
}
