resource "confluent_environment" "elc_nonprod_eastus2" {
  display_name = "elc-nonprod-eastus2"

  lifecycle {
    prevent_destroy = true
  }
}
