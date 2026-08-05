resource "confluent_kafka_cluster" "elc_nonprod_eastus2_core_enterprise" {
  display_name = "elc-nonprod-eastus2-core-enterprise"
  availability = "SINGLE_ZONE"
  cloud        = "AZURE"
  region       = "eastus2"

  enterprise {}

  environment {
    id = "env-mgzk07"
  }

  lifecycle {
    prevent_destroy = true
  }
}
