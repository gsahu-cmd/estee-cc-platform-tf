module "elc-sandbox-cc-cluster" {
  source                       = "../../../modules/cc_cluster"
  elc_mod_environment_id       = module.elc-sandbox-cc-env.environment_id
  elc_mod_cluster_name         = var.elc_cluster_name
  elc_mod_cluster_cloud        = var.elc_cluster_cloud
  elc_mod_cluster_region       = var.elc_cluster_region
  elc_mod_cluster_availability = var.elc_cluster_availability
}
