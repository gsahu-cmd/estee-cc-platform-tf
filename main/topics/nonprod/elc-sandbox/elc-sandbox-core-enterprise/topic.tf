module "confluent_kafka_topics" {
  source = "../../../../modules/cc_topic_creation"
  topics              = jsondecode(file("topics-elc-sandbox-elc--sandbox-core-enterprise.json"))
}