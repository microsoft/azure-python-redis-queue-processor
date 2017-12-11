"""
This is an unencrypted script, executed on master node.
Script prepares master node to run data processing script.

Steps:
    1. Download encrypted AES key.
    2. Download encrypted processing script.
    3. Decrypt AES key with Azure Keyvault.
    4. Decrypt script with AES key.
"""
from azure.storage.blob import BlockBlobService
from aescipher import AESCipher
from aeskeywrapper import AESKeyWrapper
from config import Config
import os
import base64
import sys

# Load configuration
# Config file is stored in /var/lib/waagent/CustomData
# File is base64 encoded
try:
    os.makedirs('config')
    with open('/var/lib/waagent/CustomData', 'rt') as file_in:
        with open('config/config.json', 'wt+') as file_out:
            base64.decode(file_in, file_out)
except:
    pass # ignore the failure if runs in docker

config = Config()

blob_service = BlockBlobService(account_name=config.storage_account_name, sas_token=config.encrypted_files_sas_token)

if not os.path.exists(config.encrypted_files_folder):
    os.makedirs(config.encrypted_files_folder)

# Download encrypted AES key
blob_service.get_blob_to_path(container_name=config.storage_container_name,
                              blob_name=config.encrypted_aes_key_filename,
                              file_path=os.path.join(config.encrypted_files_folder, config.encrypted_aes_key_filename))
encrypted_aes_key_filename = os.path.join(config.encrypted_files_folder, config.encrypted_aes_key_filename)

# Download encrypted script
blob_service.get_blob_to_path(container_name=config.storage_container_name,
                              blob_name=config.encrypted_scheduler_script_filename,
                              file_path=os.path.join(config.encrypted_files_folder, config.encrypted_scheduler_script_filename))

encrypted_script_filename = os.path.join(config.encrypted_files_folder, config.encrypted_scheduler_script_filename)
decrypted_script_filename = os.path.join(config.app_code_folder, config.unencrypted_scheduler_script_filename)

# Get blob encrypted data file from the cmd line arg
if len(sys.argv) == 2:
    blob_data_file_name = sys.argv[1]
else:
    blob_data_file_name = config.encrypted_data_filename

# Download encrypted data file
blob_service.get_blob_to_path(container_name=config.storage_container_name,
                              blob_name=blob_data_file_name,
                              file_path=os.path.join(config.encrypted_files_folder, config.encrypted_data_filename))

# Decode AES key
wrapper = AESKeyWrapper(vault = config.azure_keyvault_url,
                        client_id = config.service_principal_client_id,
                        secret = config.service_principal_secret,
                        tenant = config.tenant_id,
                        key_name = config.azure_keyvault_key_name,
                        key_version = config.azure_keyvault_key_version)

with open(encrypted_aes_key_filename, "rb") as aes_key_file:
    wrapped_key = aes_key_file.read()
    keys = wrapper.unwrap_aes_key(wrapped_key)
    key = keys[:config.aes_key_length]
    iv = keys[config.aes_key_length:]

# Decode script
aes_cipher = AESCipher(key, iv)
aes_cipher.decrypt_file_save_file(encrypted_script_filename, decrypted_script_filename)
