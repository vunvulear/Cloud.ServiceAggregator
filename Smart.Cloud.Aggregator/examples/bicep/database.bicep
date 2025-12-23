// Example Bicep Configuration
// SQL Database Example

param sqlServerName string = 'mysqlserver${uniqueString(resourceGroup().id)}'
param location string = resourceGroup().location
param administratorLogin string
@secure()
param administratorLoginPassword string
param databaseName string = 'mydb'

resource sqlServer 'Microsoft.Sql/servers@2019-06-01' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    version: '12.0'
  }
}

resource firewall 'Microsoft.Sql/servers/firewallRules@2014-04-01' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2019-06-01' = {
  parent: sqlServer
  name: databaseName
  location: location
  sku: {
    name: 'S0'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
  }
}

output sqlServerId string = sqlServer.id
output sqlServerName string = sqlServer.name
output databaseId string = sqlDatabase.id
