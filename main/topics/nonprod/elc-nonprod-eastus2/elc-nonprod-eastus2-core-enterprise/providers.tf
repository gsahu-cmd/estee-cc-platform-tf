terraform {
  required_version = "~> 1.5"  # Allows 1.5.x patches, blocks 1.6+

  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "~> 2.76"  # Allows patch updates (2.76.x), blocks 2.77+
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"  
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

provider "confluent" {
  cloud_api_key    = var.confluent_cloud_api_key
  cloud_api_secret = var.confluent_cloud_api_secret

  kafka_id                   = var.kafka_cluster_id
  kafka_rest_endpoint        = var.kafka_rest_endpoint
  kafka_api_key              = var.kafka_api_key
  kafka_api_secret           = var.kafka_api_secret
  schema_registry_id         = var.schema_registry_id
  catalog_rest_endpoint      = var.catalog_rest_endpoint
  schema_registry_api_key    = var.schema_registry_api_key
  schema_registry_api_secret = var.schema_registry_api_secret
}