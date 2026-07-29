resource "confluent_access_point" "access_point" {
  display_name = var.elc_mod_access_point_name

  environment {
    id = var.elc_mod_environment_id
  }

  gateway {
    id = var.elc_mod_gateway_id
  }

  azure_ingress_private_link_endpoint {
    private_endpoint_resource_id = var.elc_mod_private_endpoint_resource_id
  }
}
