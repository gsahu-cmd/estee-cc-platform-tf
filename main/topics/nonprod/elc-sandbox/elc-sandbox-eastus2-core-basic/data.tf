data "confluent_environment" "cc_environment" {
  id = var.environment_id
}

data "confluent_kafka_cluster" "cc_cluster" {
  id = var.kafka_cluster_id

  environment {
    id = data.confluent_environment.cc_environment.id
  }
}

data "confluent_schema_registry_cluster" "cc_schema_registry" {
  environment {
    id = data.confluent_environment.cc_environment.id
  }
}