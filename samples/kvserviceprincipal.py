# install python

# install pip https://pip.pypa.io/en/stable/installing/

# install azure keyvault sdk -> sudo pip install --ignore-installed azure-keyvault
# https://docs.microsoft.com/en-us/python/api/overview/azure/key-vault?view=azure-python

# create an Azure Service Principal for resource access
# https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal?view=azure-cli-latest

# add the service principal application to the Key Vault access policies in the Azure Portal

from azure.keyvault import KeyVaultClient, KeyVaultId
from azure.common.credentials import ServicePrincipalCredentials
from azureconfig import AzureConfig
from secrets_manager import SecretsManager

import logging

logger = logging.getLogger(__name__)

def initLogging():
    logger.setLevel(logging.DEBUG)
    # setup a console logger by default
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

if __name__ == "__main__":
    # init logging
    initLogging()

    # get the azure config and setup the creds
    config = AzureConfig()
    credentials = ServicePrincipalCredentials(
        client_id = config.client_id,
        secret = config.client_secret,
        tenant = config.tenant_id
    )

    # instantiate the client
    client = KeyVaultClient(credentials)
    secretsMgr = SecretsManager(client, config.key_vault_uri, logger)
    secretName = 'SuperSecret2'
    secret = secretsMgr.getSecret(secretName)
    
    logger.info(secret.id + " " + secret.value)