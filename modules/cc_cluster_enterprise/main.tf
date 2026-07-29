resource "confluent_kafka_cluster" "enterprise" {
  display_name = var.elc_mod_cluster_name
  availability = var.elc_mod_cluster_availability
  cloud        = var.elc_mod_cluster_cloud
  region       = var.elc_mod_cluster_region

  enterprise {
    max_ecku = var.elc_mod_cluster_max_ecku
  }

  environment {
    id = var.elc_mod_environment_id
  }

  dynamic "network" {
    for_each = var.elc_mod_network_id == null ? [] : [var.elc_mod_network_id]
    content {
      id = network.value
    }
  }

  lifecycle {
    prevent_destroy = true

    precondition {
      condition     = !(upper(replace(var.elc_mod_cluster_availability, "-", "_")) == "HIGH" && var.elc_mod_cluster_max_ecku < 2)
      error_message = "HIGH availability Enterprise clusters must have max_ecku >= 2."
    }
  }
}
