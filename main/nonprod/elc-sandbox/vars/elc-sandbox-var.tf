#azure_subscription_id = "<your-azure-subscription-id>"

# Environment Variables
elc_env_name           = "elc-sandbox"
elc_env_stream_package = "ESSENTIALS"

# Cluster Variables
elc_cluster_name         = "elc-sandbox-eastus2-core-basic"
elc_cluster_cloud        = "AZURE"
elc_cluster_region       = "eastus2"
elc_cluster_availability = "SINGLE_ZONE"

#Tags
schema_registry_id         = "lsrc-pgr69ro"
catalog_rest_endpoint      = "https://psrc-40382p5.eastus2.azure.confluent.cloud"
elc_tags = {
  "Environment"  = "Non-Production"
  "Owner"        = "ELC Confluent Team"
}
