import platform
import json
import requests
import oauth
from azureconfig import AzureConfig

appVersion = '0.1' # version of this python app
config = AzureConfig()

def getUserAgent():
    user_agent = "python/{} ({}) requests/{} app/{}".format(
        platform.python_version(),
        platform.platform(),
        requests.__version__,
        appVersion)
    return user_agent

def getAccessToken():
    #context = adal.AuthenticationContext('https://login.microsoftonline.com/' + config.tenant_id)
    #token_response = context.acquire_token_with_client_credentials('https://management.core.windows.net/', config.client_id, config.client_secret)
    
    token_response = oauth.acquire_token_with_client_credentials(
        authority = 'https://login.microsoftonline.com/' + config.tenant_id,
        resource = 'https://management.core.windows.net/', 
        clientId = config.client_id,
        secret = config.client_secret
    )
    return token_response.get('accessToken')

def httpGet(uri, accessToken):
    headers = {"Authorization": 'Bearer ' + accessToken}
    headers['User-Agent'] = getUserAgent()
    return requests.get(uri, headers=headers).json()

def buildAzureMetricsBaseUri(resourceGroup, resourceProvider, resourceType, resourceName):
    baseUri = ''.join(['https://management.azure.com',
                '/subscriptions/', config.subscription_id,
                '/resourceGroups/', resourceGroup,
                '/providers/', resourceProvider,
                '/', resourceType,
                '/', resourceName,
                '/providers/microsoft.insights/'])
    return baseUri

def getMetrics(resourceGroup, resourceProvider, resourceType, resourceName):
    baseUri = buildAzureMetricsBaseUri(resourceGroup, resourceProvider, resourceType, resourceName)
    uri = baseUri + 'metrics?api-version=2017-05-01-preview'
    accessToken = getAccessToken()
    return httpGet(uri, accessToken)

def getMetricsDefinition(resourceGroup, resourceProvider, resourceType, resourceName):
    baseUri = buildAzureMetricsBaseUri(resourceGroup, resourceProvider, resourceType, resourceName)
    uri = baseUri + 'metricDefinitions/providers/microsoft.insights/metricDefinitions?api-version=2017-05-01-preview'
    accessToken = getAccessToken()
    return httpGet(uri, accessToken)

if __name__ == "__main__":
    # Resource Providers and Types https://docs.microsoft.com/en-us/azure/monitoring-and-diagnostics/monitoring-rest-api-walkthrough#retrieve-metric-values
    # Virtual machine scale sets | Microsoft.Compute | virtualMachineScaleSets
    # VMs | Microsoft.Compute | virtualMachines

    # Get the metrics available for VM SS
    vmssMetricsDefinitionJson = getMetricsDefinition('resourcegroupname', 'Microsoft.Compute', 'virtualMachineScaleSets', 'vmssname')
    print('------------- Azure Metrics Definition Response ------------------')
    print(json.dumps(vmssMetricsDefinitionJson, sort_keys=False, indent=2, separators=(',', ': ')))

    # Get the actual perf metrics for an example VM SS
    vmssMetricsJson = getMetrics('resourcegroupname', 'Microsoft.Compute', 'virtualMachineScaleSets', 'vmssname')
    print('------------- Azure Metrics Response ------------------')
    print(json.dumps(vmssMetricsJson, sort_keys=False, indent=2, separators=(',', ': ')))

    # Get the metrics available for VMs
    vmssMetricsDefinitionJson = getMetricsDefinition('resourcegroupname', 'Microsoft.Compute', 'virtualMachines', 'vmname')
    print('------------- Azure Metrics Definition Response ------------------')
    print(json.dumps(vmssMetricsDefinitionJson, sort_keys=False, indent=2, separators=(',', ': ')))

    vmssMetricsJson = getMetrics('resourcegroupname', 'Microsoft.Compute', 'virtualMachines', 'vmname')
    print('------------- Azure Metrics Response ------------------')
    print(json.dumps(vmssMetricsJson, sort_keys=False, indent=2, separators=(',', ': ')))
