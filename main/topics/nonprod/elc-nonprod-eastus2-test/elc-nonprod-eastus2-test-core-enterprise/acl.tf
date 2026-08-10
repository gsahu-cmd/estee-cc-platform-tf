locals {
  elc_acl_file = "${path.module}/files/elc-acl.json"
  elc_acls     = fileexists(local.elc_acl_file) ? jsondecode(file(local.elc_acl_file)) : {}
}

module "cc_kafka_acls" {
  source = "../../../../../modules/cc_kafka_acls"

  elc_mod_kafka_acls = local.elc_acls
  depends_on = [module.topic_creation]
}