/*resource "confluent_tag" "master_data" {
  schema_registry_cluster {
    id = "lsrc-w7o1x0g"
  }

  rest_endpoint = "https://lsrc-w7o1x0g-ap4lgwy2.eastus2.azure.accesspoint.glb.confluent.cloud"

  credentials {
    key    = var.schema_registry_api_key
    secret = var.schema_registry_api_secret
  }

  name        = "master_data"
  description = "master data"

  lifecycle {
    prevent_destroy = true
  }
}
*/