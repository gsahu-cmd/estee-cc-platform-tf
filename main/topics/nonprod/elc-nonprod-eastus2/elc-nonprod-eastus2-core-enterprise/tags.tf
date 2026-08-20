locals {
  elc_topic_tags_file = "${path.module}/files/elc-topics-tags.json"
  elc_topic_tags      = fileexists(local.elc_topic_tags_file) ? jsondecode(file(local.elc_topic_tags_file)).topic_tags : []

  elc_topic_tag_bindings = flatten([
    for topic in local.elc_topic_tags : [
      for tag_name in topic.tags : {
        topic_name = topic.name
        tag_name   = tag_name
      }
    ]
  ])
}

module "cc_tags_bindings" {
  source = "../../../../../modules/cc_tags_bindings"

  elc_mod_topic_tag_bindings = local.elc_topic_tag_bindings
  elc_mod_schema_registry_id = var.schema_registry_id
  elc_mod_kafka_cluster_id   = data.confluent_kafka_cluster.cc_cluster.id
  depends_on = [module.topic_creation]
}