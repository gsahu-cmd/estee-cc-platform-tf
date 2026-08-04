module "cc_role_bindings" {
  source = "../../../modules/cc_role_bindings"

  elc_mod_identity_pool_role_bindings = var.elc_identity_pool_role_bindings
}
