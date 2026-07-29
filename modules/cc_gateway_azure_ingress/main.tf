resource "confluent_gateway" "gateway" {
  display_name = var.elc_mod_gateway_name
    environment {
        id = var.elc_mod_environment_id
  }
    azure_ingress_private_link_gateway {
    region = var.elc_mod_region
  }
}