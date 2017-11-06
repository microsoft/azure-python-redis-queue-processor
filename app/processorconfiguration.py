"""
This is an unencrypted script, executed on worker node.
Script prepares worker node to run processor script.

Steps:
    1. Download encrypted AES key.
"""
from azure.storage.blob import BlockBlobService
from config import Config
import os

config = Config()

blob_service = BlockBlobService(account_name=config.storage_account_name, sas_token=config.encrypted_files_sas_token)

if not os.path.exists(config.encrypted_files_folder):
    os.makedirs(config.encrypted_files_folder)

# Download encrypted AES key
blob_service.get_blob_to_path(container_name=config.storage_container_name,
                              blob_name=config.encrypted_aes_key_filename,
                              file_path=config.encrypted_files_folder + "/" + config.encrypted_aes_key_filename)
encrypted_aes_key_filename = config.encrypted_files_folder + "/" + config.encrypted_aes_key_filename
