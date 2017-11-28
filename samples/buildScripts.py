# cd <root>
# set PYTHONPATH=.
# python scripts/CopyScriptsForArmTemplate.py

import base64
import os
import tarfile
from azure.storage.blob import BlockBlobService
from app.config import Config
from app.aescipher import AESCipher
from app.aeskeywrapper import AESKeyWrapper
from app.aeshelper import AESHelper

config = Config('config/config.json')

encrypted_aes_key_filename = "data/aes.encrypted"
encrypted_script_filename = os.path.join(config.encrypted_files_folder, config.encrypted_scheduler_script_filename)

files_to_encrypt = [
    "app/scheduler.py"
]

def tar_exclusion(file):
    if not os.path.isfile(file):
        # Step into all directories
        return False

    return (file in files_to_encrypt) or (not file.endswith('py'))

# Zip up all python files under the app folder
with tarfile.open("app.tar.gz", "w:gz") as tar:
    tar.add(config.app_code_folder, recursive=True, exclude=tar_exclusion)
print 'app.tar.gz files created.'

blob_service = BlockBlobService(account_name=config.storage_account_name,
                                sas_token=config.encrypted_files_sas_token)

blob_service.create_container(container_name='app-files')
blob_service.create_blob_from_path(container_name='app-files',
                                   blob_name='app.tar.gz',
                                   file_path='app.tar.gz')
print 'app.tar.gz is uploaded'

blob_service.create_container(container_name='scheduler-node-files')
blob_service.create_blob_from_path(container_name='scheduler-node-files',
                                   blob_name='scheduler_bootstrap.sh',
                                   file_path='app/scheduler_bootstrap.sh')
print 'Scheduler_bootstrap.sh is uploaded'

blob_service.create_container(container_name='processor-node-files')
blob_service.create_blob_from_path(container_name='processor-node-files',
                                   blob_name='processor_bootstrap.sh',
                                   file_path='app/processor_bootstrap.sh')
print 'Processor_bootstrap.sh is uploaded'

# Decode AES key
aes_cipher = AESHelper(config).create_aescipher_from_config()
print 'AES key decrypted'

# Encode script
for file in files_to_encrypt:
    aes_cipher.encrypt_file_save_file(file, encrypted_script_filename)
    print file + ' is encrypted and saved to ' + encrypted_script_filename

blob_service.create_container(container_name=config.storage_container_name)
blob_service.create_blob_from_path(container_name=config.storage_container_name,
                                   blob_name=config.encrypted_scheduler_script_filename,
                                   file_path=encrypted_script_filename)
print encrypted_script_filename + " is uploaded to Azure.Storage"

# Encode config and save it locally
with open('config/config.json.encoded', 'wb+') as encoded_config_file:
    with open('config/config.json', 'r') as config_file:
        data = config_file.read()
        encoded_data = base64.encodestring(data).replace('\n', '')
        encoded_config_file.write(encoded_data)
