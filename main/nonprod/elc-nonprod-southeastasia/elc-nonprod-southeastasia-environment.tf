module "elc-nonprod-southeastasia-cc-env" {
  source = "../../../modules/cc_environment"
  elc_mod_env_name = var.elc_env_name
  elc_mod_env_stream_package = var.elc_env_stream_package
}