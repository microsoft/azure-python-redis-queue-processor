"""
AES Helper functions using config
"""
import os
from aescipher import AESCipher
from aeskeywrapper import AESKeyWrapper

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
        :return AESCipher: AESCipher objects
        """
        # Decode AES key
        wrapper = AESKeyWrapper(vault = self.config.azure_keyvault_url,
                                client_id = self.config.service_principal_client_id,
                                secret = self.config.service_principal_secret,
                                tenant = self.config.tenant_id,
                                key_name = self.config.azure_keyvault_key_name,
                                key_version = self.config.azure_keyvault_key_version)

        encrypted_aes_key_path = os.path.join(self.config.encrypted_files_folder, self.config.encrypted_aes_key_filename)
        
        with open(encrypted_aes_key_path, "rb") as aes_key_file:
            wrapped_key = aes_key_file.read()
            aes_key = wrapper.unwrap_aes_key(wrapped_key)

        return AESCipher(aes_key, self.config.aes_iv_length)