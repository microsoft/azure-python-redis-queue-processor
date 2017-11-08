"""
ES Helper functions using config
"""
import os
from app.aescipher import AESCipher
from app.aeskeywrapper import AESKeyWrapper

class AESHelper:
    """
    AES Helper functions using config
    """
    def __init__(self, config):
        """
        Initialize AESHelper class with the app.config instance
        :param app.config config: instane of config class
        """
        self.config = config


    def create_aescipher_from_config(self):
        """
        Create an AESCipher from config variables
        """
        # Decode AES key
        wrapper = AESKeyWrapper(vault = self.config.azure_keyvault_url,
                                client_id = self.config.azure_keyvault_client_id,
                                secret = self.config.azure_keyvault_secret,
                                tenant = self.config.azure_keyvault_tenant_id,
                                key_name = self.config.azure_keyvault_key_name,
                                key_version = self.config.azure_keyvault_key_version)

        encrypted_aes_key_path = os.path.join(self.config.encrypted_files_folder, self.config.encrypted_aes_key_filename)
        
        with open(encrypted_aes_key_path, "rb") as aes_key_file:
            wrapped_key = aes_key_file.read()
            keys = wrapper.unwrap_aes_key(wrapped_key)

        return AESCipher(keys[:self.config.aes_key_length], keys[self.config.aes_key_length:])