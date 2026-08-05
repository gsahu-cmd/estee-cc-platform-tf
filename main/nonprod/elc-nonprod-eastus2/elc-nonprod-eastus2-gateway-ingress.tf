/*resource "confluent_gateway" "elc_nonprod_eastus2_access_gateway" {
  display_name = "estee-sandbox-eastus2"

  environment {
    id = "env-mgzk07"
  }

  azure_ingress_private_link_gateway {
    region = "eastus2"
  }

  lifecycle {
    prevent_destroy = true
  }
}
*/