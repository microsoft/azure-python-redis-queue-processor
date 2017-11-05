# https://docs.microsoft.com/en-us/python/azure/python-sdk-azure-authenticate?view=azure-python#mgmt-auth-msi

# Enable MSI (Managed Service Identity) on VM
# Add VM Service Principal to Key Vault access via Key Vault Access Policy
# https://docs.microsoft.com/en-us/azure/active-directory/msi-tutorial-linux-vm-access-arm

from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault import KeyVaultClient
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

    # Create MSI Authentication credentials
    credentials = MSIAuthentication()
    
    # get the Azure config
    config = AzureConfig()

    # instantiate the key vault client
    client = KeyVaultClient(credentials)
    secretsMgr = SecretsManager(client, config.key_vault_uri, logger)
    secretName = 'SuperSecret2'
    secret = secretsMgr.getSecret(secretName)
    logger.info(secret.id + " " + secret.value)