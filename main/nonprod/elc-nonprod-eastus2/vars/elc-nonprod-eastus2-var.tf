#azure_subscription_id = "<your-azure-subscription-id>"

# Environment Variables
elc_env_name           = "elc-nonprod-eastus2"
elc_env_stream_package = "ESSENTIALS"

# Cluster Variables
elc_cluster_name         = "elc-nonprod-eastus2-core-enterprise"
elc_cluster_cloud        = "AZURE"
elc_cluster_region       = "eastus2"
elc_cluster_availability = "LOW"
# Kafka clusters with "HIGH" availability must have at least two eCKUs
#elc_cluster_max_ecku     = 2

# Leave this unset or set to null for deferred networking
#elc_network_id = null

#Tags
schema_registry_id         = "lsrc-pgr69ro"
catalog_rest_endpoint      = "https://psrc-40382p5.eastus2.azure.confluent.cloud"
elc_tags = {
  "Environment"  = "Non-Production"
  "Owner"        = "ELC Confluent Team"
}

#accesspoint
/*
elc_private_endpoints = {
  pe01 = {
    display_name                 = "estee-ap-nonprod-eastus2-01"
    private_endpoint_resource_id = "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Network/privateEndpoints/pe-01"
  }
  pe02 = {
    display_name                 = "estee-ap-nonprod-eastus2-02"
    private_endpoint_resource_id = "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Network/privateEndpoints/pe-02"
  }
  pe03 = {
    display_name                 = "estee-ap-nonprod-eastus2-03"
    private_endpoint_resource_id = "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Network/privateEndpoints/pe-03"
  }
}
*/