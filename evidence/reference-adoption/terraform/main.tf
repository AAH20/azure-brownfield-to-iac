terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = ">= 4.0, < 5.0" }
  }
}

provider "azurerm" { features {} }

resource "azurerm_resource_group" "rg_commerce_prod" {
  name     = "rg-commerce-prod"
  location = "westeurope"
  tags = {
    "environment" = "prod"
    "owner" = "platform"
  }
  lifecycle { prevent_destroy = true }
}

resource "azurerm_network_security_group" "nsg_checkout" {
  name                = "nsg-checkout"
  location            = "westeurope"
  resource_group_name = "rg-commerce-prod"
  tags = {
    "environment" = "prod"
  }
  lifecycle { prevent_destroy = true }
}

resource "azurerm_route_table" "rt_checkout" {
  name                = "rt-checkout"
  location            = "westeurope"
  resource_group_name = "rg-commerce-prod"
  bgp_route_propagation_enabled = true
  tags = {
    "environment" = "prod"
  }
  lifecycle { prevent_destroy = true }
}

resource "azurerm_virtual_network" "vnet_commerce" {
  name                = "vnet-commerce"
  location            = "westeurope"
  resource_group_name = "rg-commerce-prod"
  address_space = ["10.40.0.0/16"]
  tags = {
    "cost-center" = "digital-sales"
    "environment" = "prod"
  }
  lifecycle { prevent_destroy = true }
}

resource "azurerm_private_dns_zone" "privatelink_blob_core_windows_net" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = "rg-commerce-prod"
  tags = {
    "environment" = "prod"
  }
  lifecycle { prevent_destroy = true }
}

resource "azurerm_log_analytics_workspace" "law_commerce_prod" {
  name                = "law-commerce-prod"
  location            = "westeurope"
  resource_group_name = "rg-commerce-prod"
  sku               = "PerGB2018"
  retention_in_days = 30
  tags = {
    "environment" = "prod"
  }
  lifecycle { prevent_destroy = true }
}

resource "azurerm_storage_account" "stcommerceprod01" {
  name                = "stcommerceprod01"
  location            = "westeurope"
  resource_group_name = "rg-commerce-prod"
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  tags = {
    "data-class" = "confidential"
    "environment" = "prod"
  }
  lifecycle { prevent_destroy = true }
}
