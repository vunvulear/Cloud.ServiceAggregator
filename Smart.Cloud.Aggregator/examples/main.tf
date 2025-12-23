terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "rg-smartcloud-prod"
  location = "East US"
}

# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "stsmartcloudprod"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
}

# Blob Storage Container
resource "azurerm_storage_container" "data" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "vnet-smartcloud"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# Subnet
resource "azurerm_subnet" "internal" {
  name                 = "subnet-internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Network Security Group
resource "azurerm_network_security_group" "main" {
  name                = "nsg-smartcloud"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

# Public IP
resource "azurerm_public_ip" "main" {
  name                = "pip-smartcloud"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
}

# SQL Server
resource "azurerm_sql_server" "main" {
  name                         = "sqlsrv-smartcloud"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = "P@ssw0rd1234567890"
}

# SQL Database
resource "azurerm_sql_database" "main" {
  name                = "sqldb-smartcloud"
  resource_group_name = azurerm_resource_group.main.name
  server_name         = azurerm_sql_server.main.name
  edition             = "Standard"
  collation           = "SQL_Latin1_General_CP1_CI_AS"
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                       = "kv-smartcloud"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  enabled_for_disk_encryption = true
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "premium"
}

# App Service Plan
resource "azurerm_app_service_plan" "main" {
  name                = "appplan-smartcloud"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Standard"
    size = "S1"
  }
}

# App Service
resource "azurerm_app_service" "main" {
  name                = "app-smartcloud"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  app_service_plan_id = azurerm_app_service_plan.main.id
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-smartcloud"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "ai-smartcloud"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
}

# Data source
data "azurerm_client_config" "current" {}
