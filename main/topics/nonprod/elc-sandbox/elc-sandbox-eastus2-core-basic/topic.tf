module "topic_creation" {
  source = "../../../../../modules/cc_topic_creation"
  topics              = jsondecode(file("topics-elc-sandbox-elc-sandbox-eastus2-core-basic.json"))
  rest_endpoint    = var.catalog_rest_endpoint
}