resource "confluent_environment" "elc-environment" {
  display_name = var.elc_mod_env_name

  stream_governance {
    package = var.elc_mod_env_stream_package # "ESSENTIALS"
  }


  lifecycle {
    prevent_destroy = true
  }

}