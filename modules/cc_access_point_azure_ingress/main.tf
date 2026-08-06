resource "confluent_access_point" "access_point" {
  for_each = var.elc_mod_private_endpoints

  display_name = each.value.elc_mod_display_name

  environment {
    id = var.elc_mod_environment_id
  }

  gateway {
    id = var.elc_mod_gateway_id
  }

  depends_on = [
    confluent_gateway.gateway
  ]

  azure_ingress_private_link_endpoint {
    private_endpoint_resource_id = each.value.elc_mod_private_endpoint_resource_id
  }
}
