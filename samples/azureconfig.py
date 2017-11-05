class AzureConfig(object):
    """
    Configuration settings for use in sample code.  Users wishing to run this sample can either set these
    values as environment values or simply update the hard-coded values below

    :ivar subscription_name: Azure subscription name
    :vartype subscription_name: str

    :ivar resource_group: Azure resource group containing the infra
    :vartype resource_group: str
    
    :ivar client_id: Azure Active Directory AppID of the Service Principle to run the sample
    :vartype client_id: str

    :ivar tenant_id: Azure Active Directory tenant id of the user intending to run the sample
    :vartype tenant_id: str

    :ivar client_secret: Azure Active Directory Application Key to run the sample
    :vartype client_secret: str

    :ivar key_vault_uri: URI for Azure Key Vault instance
    :vartype key_vault_uri: str
    """

    def __init__(self):
        # Azure Subscription Name
        self.subscription_name = ''

        # Subscription Id
        self.subscription_id = ''

        # Azure Resource Group
        self.resource_group = ''

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