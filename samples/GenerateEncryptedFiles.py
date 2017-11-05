import os
import random
import string
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from app.aescipher import AESCipher
from app.aeskeywrapper import AESKeyWrapper
from app.config import Config
config = Config()

script_filename = "app/scheduler.py"
unencrypted_records_file = 'data/data'
script_encrypted_filename = config.encrypted_files_folder + "/" + config.encrypted_scheduler_script_filename
aes_key_encrypted_filename = config.encrypted_files_folder + "/" + config.encrypted_aes_key_filename
encrypted_record_file = config.encrypted_files_folder + "/" + config.encrypted_data_filename



wrapper = AESKeyWrapper(vault = config.azure_keyvault_url,
                        client_id = config.azure_keyvault_client_id,
                        secret = config.azure_keyvault_secret,
                        tenant = config.azure_keyvault_tenant_id,
                        key_name = config.azure_keyvault_key_name,
                        key_version = config.azure_keyvault_key_version)

# Generate new key\iv pair
aes_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
aes_iv = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
keys = aes_key + aes_iv

print 'AES key generated. Key:' + aes_key + " IV:" + aes_iv

# Save encrypted keys
encrypted_keys = wrapper.wrap_aes_key_local(keys, wrapper.get_public_key())
with open(aes_key_encrypted_filename, "wb+") as aes_key_encrypted_file:
    aes_key_encrypted_file.write(encrypted_keys)
print 'AES key wrapped and saved to ' + aes_key_encrypted_filename

# Encrypt script using generated keys
cipher = AESCipher(aes_key, aes_iv)
cipher.encrypt_file_save_file(script_filename, script_encrypted_filename)
print script_filename + " encrypted and saved to " + script_encrypted_filename

# Encrypt data
with open(encrypted_record_file, 'wb') as encryptedFile:
    with open(unencrypted_records_file, 'r') as dataFile:
            for record in dataFile:
                encryptedRecord = cipher.encrypt(record)
                encryptedFile.writelines(encryptedRecord+'\n')

print unencrypted_records_file + " is encrypted and saved to " + encrypted_record_file

# Upload generated files to blob
blob_service = BlockBlobService(account_name=config.storage_account_name, sas_token=config.encrypted_files_sas_token)

blob_service.create_container(config.storage_container_name)

blob_service.create_blob_from_path(container_name=config.storage_container_name,
                                   blob_name=config.encrypted_aes_key_filename,
                                   file_path=aes_key_encrypted_filename)

blob_service.create_blob_from_path(container_name=config.storage_container_name,
                                   blob_name=config.encrypted_scheduler_script_filename,
                                   file_path=script_encrypted_filename)

blob_service.create_blob_from_path(container_name=config.storage_container_name,
                                   blob_name=config.encrypted_data_filename,
                                   file_path=encrypted_record_file)
print "Files succesfully uploaded to Azure.Storage"
