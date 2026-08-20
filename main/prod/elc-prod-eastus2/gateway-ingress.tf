module "elc-prod-eastus2-cc-ingress-gateway" {
  source = "../../../modules/cc_gateway_azure_ingress"

  elc_mod_gateway_name = var.elc_ingress_gateway_name
  elc_mod_region       = var.elc_cluster_region
  elc_mod_environment_id       = module.elc-nonprod-eastus2-cc-env.environment_id
}
