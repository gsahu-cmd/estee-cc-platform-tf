terraform {
  required_version = "~> 1.5"

  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = "~> 2.76"
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
}