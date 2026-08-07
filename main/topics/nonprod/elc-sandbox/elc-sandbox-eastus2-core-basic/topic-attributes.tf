locals {
  elc_topic_attributes_file = "${path.module}/files/elc-topic-attributes.json"
  elc_topic_attributes      = fileexists(local.elc_topic_attributes_file) ? jsondecode(file(local.elc_topic_attributes_file)) : {}
}

module "cc_topic_catalog_attributes" {
  source = "../../../../../modules/cc_topic_catalog_attributes"

  elc_mod_topic_catalog_attributes = local.elc_topic_attributes
  elc_mod_kafka_cluster_id         = data.confluent_kafka_cluster.cc_cluster.id
  depends_on = [module.topic_creation]
}