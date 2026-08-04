resource "confluent_environment" "elc_sandbox_eastus2" {
  display_name = "estee-sandbox-eastus2"

  lifecycle {
    prevent_destroy = true
  }
}
