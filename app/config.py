"""
    config.py only contains the configuration class
"""
import os

class Config(object):
    """
    This class contains configuration parameters for all applications
    """
    def __init__(self):
        # Job Status storage account name
        self.job_status_storage = ''

        # Job Status storage SAS token
        self.job_status_sas_token = '

        # Azure Subscription
        self.subscription_name = ''
        self.subscription_id = ''

        # Encrypted files storage SAS token
        self.encrypted_files_sas_token = ''
        self.storage_account_name = ''
        self.storage_container_name = ''

        # File names
        self.encrypted_aes_key_filename = ''
        self.encrypted_scheduler_script_filename = ''
        self.encrypted_files_folder = ''
        self.scheduler_script_filename = ''
        self.encrypted_data_filename = ''

        # AES key configuration
        self.aes_key_length = 32

        # Azure keyvault configuration
        self.azure_keyvault_url = ''
        self.azure_keyvault_client_id = ''
        self.azure_keyvault_secret = ''
        self.azure_keyvault_tenant_id = ''
        self.azure_keyvault_key_name = 'RSAKey'
        self.azure_keyvault_key_version = ''

        # Azure Active Directory - Directory ID in Azure portal
        self.tenant_id = ''

        # Your Service Principal Application ID in Azure Portal
        self.client_id = ''

        # Application Key Value in Azure Portal
        self.client_secret = ''

        # Your Key Vault URI
        self.key_vault_uri = ''

        #Key vault API version
        self.key_vault_api_version = '2016-10-01'
        
        # Redis Q Host Address
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')

        # Redis Q Port
        self.redis_port = os.getenv('REDIS_PORT', 6379)
        
        #Logger Queue Name
        self.logger_queue_name = ''

        #Logger Queue Storage Account Name
        self.logger_storage_account_name=''

        # Logger Queue SAS
        self.logger_queue_sas =''

        # Metrics configuration
        self.vm_resource_group = ''
        self.metrics_storage = ''
        self.metrics_sas_token = ''