module "elc_nonprod_eastus2_tags" {
  source = "../../../modules/cc_tags"

  elc_mod_tags = var.elc_tags
}