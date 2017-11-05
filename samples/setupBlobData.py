# Grab the primary key
# Execute from parent folder of scripts and apps: PYTHONPATH=. python scripts/setupBlobData.py
from azure.storage.blob import BlockBlobService
from app.config import Config
from app.aescipher import AESCipher
from app.aeskeywrapper import AESKeyWrapper
import logging

logger = logging.getLogger(__name__)

BLOB_NAME = 'processingData'

def initLogging():
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

if __name__ == "__main__":
    # init logging
    initLogging()

    unencrypted_records_file = 'data/data'
    encrypted_record_file = 'data/data.encrypted'
    downloaded_encrypted_record_file = 'data/data.dl.encrypted'

    config = Config()

    # Download encrypted AES key
    encrypted_aes_key_filename = "data/aes.encrypted"

    # Decode AES key
    wrapper = AESKeyWrapper(vault = config.azure_keyvault_url,
                            client_id = config.azure_keyvault_client_id,
                            secret = config.azure_keyvault_secret,
                            tenant = config.azure_keyvault_tenant_id,
                            key_name = config.azure_keyvault_key_name,
                            key_version = config.azure_keyvault_key_version)

    with open(encrypted_aes_key_filename, "rb") as aes_key_file:
        wrapped_key = aes_key_file.read()
        keys = wrapper.unwrap_aes_key(wrapped_key)
        key = keys[:config.aes_key_length]
        iv = keys[config.aes_key_length:]

    aes_cipher = AESCipher(key, iv)

    # encrypt file records
    encryptedData = aes_cipher.encrypt_file(unencrypted_records_file)

    with open(encrypted_record_file, 'wb') as encryptedFile:
        with open(unencrypted_records_file, 'r') as dataFile:
                for record in dataFile:
                    encryptedRecord = aes_cipher.encrypt(record)
                    encryptedFile.writelines(encryptedRecord+'\n')

    # instantiate the client
    blob_service = BlockBlobService(account_name=config.storage_account_name, account_key=config.storage_account_key)

    # create container
    blob_service.create_container(config.storage_container_name)
    
    # upload file
    blob_service.create_blob_from_path(config.storage_container_name, BLOB_NAME, encrypted_record_file) 

    # download file
    blob_service.get_blob_to_path(container_name=config.storage_container_name, blob_name=BLOB_NAME, file_path=downloaded_encrypted_record_file)

    # decrypt file records
    with open(downloaded_encrypted_record_file, 'rb') as encryptedFile:
        for record in encryptedFile:
            print aes_cipher.decrypt(record.rstrip('\n'))