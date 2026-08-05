resource "confluent_access_point" "elc_nonprod_eastus2_access_point" {
  display_name = "estee-sandbox-eastus2"

  environment {
    id = "env-mgzk07"
  }

  gateway {
    id = "gw-ov05ww"
  }

  azure_ingress_private_link_endpoint {
    private_endpoint_resource_id = "/subscriptions/3c33b258-6a1b-498c-9dd7-2e4b52ff16dc/resourceGroups/RG-AM-EastUS-NonProd-EIS-EIP01/providers/Microsoft.Network/privateEndpoints/PE-AM-EastUS-NonProd-EIP"
  }

  lifecycle {
    prevent_destroy = true
  }
}
