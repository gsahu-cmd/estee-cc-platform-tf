module "confluent_kafka_topics" {
  source = "../../../../modules/cc_topic_creation"
  topics              = jsondecode(file("topics-elc-nonprod-eastus2-elc-nonprod-eastus2-core-enterprise.json"))
}