resource "confluent_kafka_cluster" "basic" {
  display_name     = var.elc_mod_cluster_name
  availability     = var.elc_mod_cluster_availability
  cloud            = var.elc_mod_cluster_cloud
  region           = var.elc_mod_cluster_region
  basic {}

  environment {
    id = var.elc_mod_environment_id
  }

  lifecycle {
    prevent_destroy = true
  }
}