resource "confluent_kafka_cluster" "dedicated" {
  display_name = var.elc_mod_cluster_name
  availability = var.elc_mod_cluster_availability
  cloud        = var.elc_mod_cluster_cloud
  region       = var.elc_mod_cluster_region

  dedicated {
    cku = var.elc_mod_cluster_cku
  }

  environment {
    id = var.elc_mod_environment_id
  }

  lifecycle {
    prevent_destroy = true
  }

  # Uncomment this block only if you are using private networking
  # and already created a Confluent Cloud network.
  #
  # network {
  #   id = var.elc_mod_network_id
  # }
}
