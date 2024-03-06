// ========== main.bicep ========== //
targetScope = 'resourceGroup'

@minLength(3)
@maxLength(6)
@description('Prefix Name')
param solutionPrefix string


var solutionLocation = resourceGroup().location

var baseUrl = 'https://raw.githubusercontent.com/nchandhi/nctestrepo/main/' //'https://github.com/nchandhi/nctestrepo/blob/main/' //'https://tmpstrgtst.blob.core.windows.net/'


// param appServicePlanName string = ''
// var resourceToken = toLower(uniqueString(subscription().id, solutionPrefix, solutionLocation))
// var tags = { 'azd-env-name': solutionPrefix }


// // Create an App Service Plan to group applications under the same payment plan and SKU
// module appServicePlan '1_depoy_appservice_plan.bicep' = {
//   name: 'depoy_appservice_plan'
//   scope: resourceGroup(resourceGroup().name)
//   params: {
//     name: !empty(appServicePlanName) ? appServicePlanName : 'plan-${resourceToken}'
//     location: solutionLocation
//     tags: tags
//     sku: {
//       name: 'B1'
//       capacity: 1
//     }
//     kind: 'linux'
//   }
// }

// param backendServiceName string = ''
// // Used for the Azure AD application
// param authClientId string
// @secure()
// param authClientSecret string

// // The application frontend
// var appServiceName = !empty(backendServiceName) ? backendServiceName : 'app-backend-${resourceToken}'
// var authIssuerUri = '${environment().authentication.loginEndpoint}${tenant().tenantId}/v2.0'
// module backend '1_deploy_appservice.bicep' = {
//   name: 'web'
//   scope: resourceGroup(resourceGroup().name)
//   params: {
//     name: appServiceName
//     location: solutionLocation
//     tags: union(tags, { 'azd-service-name': 'backend' })
//     appServicePlanId: appServicePlan.outputs.id
//     runtimeName: 'python'
//     runtimeVersion: '3.10'
//     scmDoBuildDuringDeployment: true
//     managedIdentity: true
//     authClientSecret: authClientSecret
//     authClientId: authClientId
//     authIssuerUri: authIssuerUri
//     appSettings: {
//       // search
//       AZURE_SEARCH_INDEX: 'testsearchindex'
//     }
//   }
// }


// // ========== Managed Identity ========== //
// module managedIdentityModule 'deploy_managed_identity.bicep' = {
//   name: 'deploy_managed_identity'
//   params: {
//     solutionName: solutionPrefix
//     solutionLocation: solutionLocation
//   }
//   scope: resourceGroup(resourceGroup().name)
// }


// // ========== Storage Account Module ========== //
// module storageAccountModule 'deploy_storage_account.bicep' = {
//   name: 'deploy_storage_account.bicep'
//   params: {
//     solutionName: solutionPrefix
//     solutionLocation: solutionLocation
//     managedIdentityObjectId:managedIdentityModule.outputs.managedIdentityOutput.objectId
//   }
//   scope: resourceGroup(resourceGroup().name)
// }

// // ========== Azure AI services multi-service account ========== //
// module azAIMultiServiceAccount 'deploy_azure_ai_service.bicep' = {
//   name: 'deploy_azure_ai_service'
//   params: {
//     solutionName: solutionPrefix
//     solutionLocation: solutionLocation
//   }
// } 

// // ========== Search service ========== //
// module azSearchService 'deploy_ai_search_service.bicep' = {
//   name: 'deploy_ai_search_service'
//   params: {
//     solutionName: solutionPrefix
//     solutionLocation: solutionLocation
//   }
// } 

// // ========== Azure OpenAI ========== //
// module azOpenAI 'deploy_azure_open_ai.bicep' = {
//   name: 'deploy_azure_open_ai'
//   params: {
//     solutionName: solutionPrefix
//     solutionLocation: solutionLocation
//   }
// }

// module uploadFiles 'deploy_upload_files_script.bicep' = {
//   name : 'deploy_upload_files_script'
//   params:{
//     storageAccountName:storageAccountModule.outputs.storageAccountOutput.name
//     solutionLocation: solutionLocation
//     containerName:storageAccountModule.outputs.storageAccountOutput.dataContainer
//     identity:managedIdentityModule.outputs.managedIdentityOutput.id
//     storageAccountKey:storageAccountModule.outputs.storageAccountOutput.key
//     baseUrl:baseUrl
//   }
//   dependsOn:[storageAccountModule]
// }

// // ========== Key Vault ========== //

// module keyvaultModule 'deploy_keyvault.bicep' = {
//   name: 'deploy_keyvault'
//   params: {
//     solutionName: solutionPrefix
//     solutionLocation: solutionLocation
//     objectId: managedIdentityModule.outputs.managedIdentityOutput.objectId
//     tenantId: subscription().tenantId
//     managedIdentityObjectId:managedIdentityModule.outputs.managedIdentityOutput.objectId
//     adlsAccountName:storageAccountModule.outputs.storageAccountOutput.storageAccountName
//     adlsAccountKey:storageAccountModule.outputs.storageAccountOutput.key
//     adlsStoreName:storageAccountModule.outputs.storageAccountOutput.storageAccountName
//     openApiType:'azure'
//     azureOpenAIApiKey:azOpenAI.outputs.openAIOutput.openAPIKey
//     azureOpenAIApiVersion:'2023-07-01-preview'
//     azureOpenAIEndpoint:azOpenAI.outputs.openAIOutput.openAPIEndpoint
//     azureSearchAdminKey:azSearchService.outputs.searchServiceOutput.searchServiceAdminKey
//     azureSearchServiceEndpoint:azSearchService.outputs.searchServiceOutput.searchServiceEndpoint
//     cogServiceEndpoint:azAIMultiServiceAccount.outputs.cogSearchOutput.cogServiceEndpoint
//     cogServiceName:azAIMultiServiceAccount.outputs.cogSearchOutput.cogServiceName
//     cogServiceKey:azAIMultiServiceAccount.outputs.cogSearchOutput.cogServiceKey
//     enableSoftDelete:false
//   }
//   scope: resourceGroup(resourceGroup().name)
//   dependsOn:[storageAccountModule,azOpenAI,azAIMultiServiceAccount,azSearchService]
// }

// module createIndex 'deploy_python_scripts.bicep' = {
//   name : 'deploy_python_scripts'
//   params:{
//     solutionLocation: solutionLocation
//     identity:managedIdentityModule.outputs.managedIdentityOutput.id
//     baseUrl:baseUrl
//     keyVaultName:keyvaultModule.outputs.keyvaultOutput.name
//   }
//   dependsOn:[keyvaultModule]
// }

// // module deployPVA 'deploy_pva_sol.bicep' = {
// //   name : 'deploy_pva_sol'
// //   params:{
// //     solutionLocation: solutionLocation
// //     identity:managedIdentityModule.outputs.managedIdentityOutput.id
// //     baseUrl:baseUrl
// //     applicationId:clientId
// //     clientSecret:clientSecret
// //     environmentId:environmentId
// //     environmentUrl:environmentUrl
// //     tenant:tenant().tenantId
// //   }
// //   dependsOn:[storageAccountModule]
// // }

// // module deployPVAConnection 'deploy_pva_connection.bicep' = {
// //   name : 'deploy_pva_connection'
// //   params:{
// //     azureOpenAIApiVersion:'2023-06-01-preview'
// //     azureOpenAIDeploymentId:'gpt-35-turbo'
// //     azureSearchQueryType:'simple'
// //     searchIndexName:'ncprinterindex3'
// //     openAIAccountName:azOpenAI.outputs.openAIOutput.openAIAccountName
// //     environment:environmentId
// //     searchService_name:azSearchService.outputs.searchServiceOutput.searchServiceName
// //   }
// //   dependsOn:[deployPVA,createIndex]
// // }

