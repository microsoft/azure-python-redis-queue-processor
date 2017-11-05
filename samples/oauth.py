# install python
# >>> pip install requests

# sample object returned by the acquire_token_with_client_credentials method
#{
#    'tokenType': 'Bearer',
#    'expiresIn': 3600,
#    'expiresOn': '2017-10-30 12:56:39.436417',
#    'resource': '<Resource>',
#    'accessToken': '<Token>',
#    'isMRRT': True,
#    '_clientId': '<ClientId>',
#    '_authority': 'Authority'
#}

import requests
from azureconfig import AzureConfig
config = AzureConfig()


# all requests are posted through this method. Replace this single method if reqeusts is not available.
def post_request(url, headers, body):
    response = requests.post(url, headers=headers, data=body)
    return response


def acquire_token_with_client_credentials(authority, resource, clientId, secret):
    url = authority + '/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'} 
    body = {'grant_type':'client_credentials'}
    body['client_id'] = clientId
    body['client_secret'] = secret
    body['resource'] = resource
    response = post_request(url, headers, body)    

    token = {'tokenType' : response.json()['token_type']}
    token['expiresIn'] = response.json()['expires_in']
    token['expiresOn'] = response.json()['expires_on']
    token['resource'] = response.json()['resource']
    token['accessToken'] = response.json()['access_token']
    token['isMRRT'] = True #TODO: Replace hard coded value
    token['_clientId'] = clientId
    token['_authority'] = authority
    return token


if __name__ == '__main__':
    tenantId = config.tenant_id # Azure Active Directory - Directory ID in Azure portal
    clientId = config.client_id # Application ID in Azure Portal
    clientSecret = config.client_secret # Application Key Value in Azure Portal

    url = 'https://login.microsoftonline.com/' + tenantId
    token = acquire_token_with_client_credentials(url, 'https://management.core.windows.net/', clientId, clientSecret)
    print(token)
