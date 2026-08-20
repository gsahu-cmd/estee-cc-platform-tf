module "topic_creation" {
  source = "../../../../../modules/cc_topic_creation"

  topics = jsondecode(file("${path.module}/files/elc-topics.json"))
}