// ========== main.bicep ========== //
targetScope = 'resourceGroup'

@minLength(3)
@maxLength(6)
@description('Prefix Name')
param solutionPrefix string

// param clientId string
// @secure()
// param clientSecret string
// param environmentUrl string
// param environmentId string

var solutionLocation = resourceGroup().location

var baseUrl = 'https://raw.githubusercontent.com/nchandhi/nctestrepo/main/' //'https://github.com/nchandhi/nctestrepo/blob/main/' //'https://tmpstrgtst.blob.core.windows.net/'

// ========== Managed Identity ========== //
module managedIdentityModule 'deploy_managed_identity.bicep' = {
  name: 'deploy_managed_identity'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
  }
  scope: resourceGroup(resourceGroup().name)
}


// ========== Storage Account Module ========== //
module storageAccountModule 'deploy_storage_account.bicep' = {
  name: 'deploy_storage_account.bicep'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
    managedIdentityObjectId:managedIdentityModule.outputs.managedIdentityOutput.objectId
  }
  scope: resourceGroup(resourceGroup().name)
}

// ========== Azure AI services multi-service account ========== //
module azAIMultiServiceAccount 'deploy_azure_ai_service.bicep' = {
  name: 'deploy_azure_ai_service'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
  }
} 

// ========== Search service ========== //
module azSearchService 'deploy_ai_search_service.bicep' = {
  name: 'deploy_ai_search_service'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
  }
} 

// ========== Azure OpenAI ========== //
module azOpenAI 'deploy_azure_open_ai.bicep' = {
  name: 'deploy_azure_open_ai'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
  }
}

module uploadFiles 'deploy_upload_files_script.bicep' = {
  name : 'deploy_upload_files_script'
  params:{
    storageAccountName:storageAccountModule.outputs.storageAccountOutput.name
    solutionLocation: solutionLocation
    containerName:storageAccountModule.outputs.storageAccountOutput.dataContainer
    identity:managedIdentityModule.outputs.managedIdentityOutput.id
    storageAccountKey:storageAccountModule.outputs.storageAccountOutput.key
    baseUrl:baseUrl
  }
  dependsOn:[storageAccountModule]
}

// ========== Key Vault ========== //

// clientId:clientId
// clientSecret:clientSecret
// environmentUrl:environmentUrl
// environmentId:environmentId

module keyvaultModule 'deploy_keyvault.bicep' = {
  name: 'deploy_keyvault'
  params: {
    solutionName: solutionPrefix
    solutionLocation: solutionLocation
    objectId: managedIdentityModule.outputs.managedIdentityOutput.objectId
    tenantId: subscription().tenantId
    managedIdentityObjectId:managedIdentityModule.outputs.managedIdentityOutput.objectId
    adlsAccountName:storageAccountModule.outputs.storageAccountOutput.storageAccountName
    adlsAccountKey:storageAccountModule.outputs.storageAccountOutput.key
    adlsStoreName:storageAccountModule.outputs.storageAccountOutput.storageAccountName
    openApiType:'azure'
    azureOpenAIApiKey:azOpenAI.outputs.openAIOutput.openAPIKey
    azureOpenAIApiVersion:'2023-07-01-preview'
    azureOpenAIEndpoint:azOpenAI.outputs.openAIOutput.openAPIEndpoint
    azureSearchAdminKey:azSearchService.outputs.searchServiceOutput.searchServiceAdminKey
    azureSearchServiceEndpoint:azSearchService.outputs.searchServiceOutput.searchServiceEndpoint
    cogServiceEndpoint:azAIMultiServiceAccount.outputs.cogSearchOutput.cogServiceEndpoint
    cogServiceName:azAIMultiServiceAccount.outputs.cogSearchOutput.cogServiceName
    cogServiceKey:azAIMultiServiceAccount.outputs.cogSearchOutput.cogServiceKey
    enableSoftDelete:false
  }
  scope: resourceGroup(resourceGroup().name)
  dependsOn:[storageAccountModule,azOpenAI,azAIMultiServiceAccount,azSearchService]
}

module createIndex 'deploy_python_scripts.bicep' = {
  name : 'deploy_python_scripts'
  params:{
    solutionLocation: solutionLocation
    identity:managedIdentityModule.outputs.managedIdentityOutput.id
    baseUrl:baseUrl
    keyVaultName:keyvaultModule.outputs.keyvaultOutput.name
  }
  dependsOn:[keyvaultModule]
}

// module deployPVA 'deploy_pva_sol.bicep' = {
//   name : 'deploy_pva_sol'
//   params:{
//     solutionLocation: solutionLocation
//     identity:managedIdentityModule.outputs.managedIdentityOutput.id
//     baseUrl:baseUrl
//     applicationId:clientId
//     clientSecret:clientSecret
//     environmentId:environmentId
//     environmentUrl:environmentUrl
//     tenant:tenant().tenantId
//   }
//   dependsOn:[storageAccountModule]
// }

// module deployPVAConnection 'deploy_pva_connection.bicep' = {
//   name : 'deploy_pva_connection'
//   params:{
//     azureOpenAIApiVersion:'2023-06-01-preview'
//     azureOpenAIDeploymentId:'gpt-35-turbo'
//     azureSearchQueryType:'simple'
//     searchIndexName:'ncprinterindex3'
//     openAIAccountName:azOpenAI.outputs.openAIOutput.openAIAccountName
//     environment:environmentId
//     searchService_name:azSearchService.outputs.searchServiceOutput.searchServiceName
//   }
//   dependsOn:[deployPVA,createIndex]
// }

