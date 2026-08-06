/*resource "confluent_gateway" "elc_nonprod_eastus2_access_gateway" {
  display_name = var.elc_ingress_gateway_name

  environment {
    id = module.elc-nonprod-eastus2-cc-env.environment_id
  }

  azure_ingress_private_link_gateway {
    region = var.elc_cluster_region
  }

  lifecycle {
    prevent_destroy = true
  }
}
*/