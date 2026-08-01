module "topic_creation" {
  source = "../../../../modules/cc_topic_creation"
  topics              = jsondecode(file("topics-estee-sandbox-eastus2-estee-sandbox-eastus2-core-enterprise.json"))
}