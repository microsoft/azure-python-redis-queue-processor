class SecretsManager(object):

    def __init__(self, secretsClient, secretStoreUri, logger):
        self.client = secretsClient
        self.secret_store_uri = secretStoreUri
        self.logger = logger

    def logException(self, exception, functionName):
        self.logger.debug("Exception occurred in: " + functionName)
        self.logger.debug(type(exception))
        self.logger.debug(exception)

    def getKey(self, name):
        try:
            # Read a key without version
            key = self.client.get_key(self.secret_store_uri, name, '')
            return key
        except Exception as ex:
            self.logException(ex, self.getKey.__name__)

    def getSecretVersions(self, name):
        # Print a list of versions for a secret
        versions = self.client.get_secret_versions(self.secret_store_uri, name)
        for version in versions:
            print(version.id) 

    def getSecret(self, name):
        # Read a secret without version
        try:
            secret = self.client.get_secret(self.secret_store_uri, name, '')
            return secret
        except Exception as ex:
            self.logException(ex, self.getSecret.__name__)

    def setSecret(self, name, value):
        # adds a secret to the Azure Key Vault. If the named secret already exists, Azure Key Vault creates a new version of that secret.
        self.client.set_secret(self.secret_store_uri, name, value)

    def disableSecret(self, name):
        # Update a secret without version
        self.client.update_secret(self.secret_store_uri, name, '', secret_attributes={'enabled': False})

    def enableSecret(self, name):
        # Update a secret without version
        self.client.update_secret(self.secret_store_uri, name, '', secret_attributes={'enabled': True})

'''
# Create a key
key_bundle = self.client.create_key(self.secret_store_uri, 'FirstKey', 'RSA')
key_id = KeyVaultId.parse_key_id(key_bundle.key.kid)

# Update a key without version
client.update_key(key_id.vault, key_id.name, key_id.version_none, key_attributes={'enabled': False})

# Update a key with version
client.update_key(key_id.vault, key_id.name, key_id.version, key_attributes={'enabled': False})

# Print a list of versions for a key
versions = self.client.get_key_versions(self.secret_store_uri, 'FirstKey')
for version in versions:
    print(version.kid)  # https://myvault.vault.azure.net/keys/FirstKey/000102030405060708090a0b0c0d0e0f

# Read a key with version
client.get_key(key_id.vault, key_id.name, key_id.version)

# Delete a key
self.client.delete_key(self.secret_store_uri, 'FirstKey')

# Create a secret
secret_bundle = self.client.set_secret(self.secret_store_uri, 'FirstSecret', 'Hush, that is secret!!')
secret_id = KeyVaultId.parse_secret_id(secret_bundle.id)

# Update a secret with version
self.client.update_key(secret_id.vault, secret_id.name, secret_id.version, secret_attributes={'enabled': False})

# Read a secret with version
self.client.get_secret(secret_id.vault, secret_id.name, secret_id.version)

# Delete a secret
self.client.delete_secret(self.secret_store_uri, 'FirstSecret')
'''