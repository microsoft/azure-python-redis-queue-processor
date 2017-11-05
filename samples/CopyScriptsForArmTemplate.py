# cd <root>
# set PYTHONPATH=.
# python scripts/CopyScriptsForArmTemplate.py

from azure.storage.blob import BlockBlobService
from app.config import Config
from app.aescipher import AESCipher
from app.aeskeywrapper import AESKeyWrapper
import tarfile
import os

config = Config()

encrypted_aes_key_filename = "data/aes.encrypted"
unencrypted_script_filename = "app/scheduler.py"
encrypted_script_filename = config.encrypted_files_folder + "/" + config.encrypted_scheduler_script_filename


basescripts = [
    'config.py',
    'aescipher.py',
    'aeskeywrapper.py',
    'functions.py',
    'jobstatus.py',
]

processorscripts = [
    'processorconfiguration.py',
    'processor.py',
]

schedulerscripts = [
    'schedulerconfiguration.py',
]

os.chdir('app')
print 'Preparing ProcessorScripts.tar.gz...'
with tarfile.open("../processorscripts.tar.gz", "w:gz") as tar:
    for script in basescripts + processorscripts:
        tar.add(name=script)
        print '    +' + script

print 'Preparing SchedulerScripts.tar.gz...'
with tarfile.open("../schedulerscripts.tar.gz", "w:gz") as tar:
    for script in basescripts + schedulerscripts:
        tar.add(name=script)
        print '    +' + script

print 'tar.gz files created.'
os.chdir('..')

blob_service = BlockBlobService(account_name=config.storage_account_name, sas_token=config.encrypted_files_sas_token)

blob_service.create_container(container_name = 'scheduler-node-files')

blob_service.create_blob_from_path(container_name='scheduler-node-files',
                                   blob_name='scheduler_bootstrap.sh',
                                   file_path='app/scheduler_bootstrap.sh')
print 'Scheduler_bootstrap.sh is uploaded'

blob_service.create_blob_from_path(container_name='scheduler-node-files',
                                   blob_name='schedulerscripts.tar.gz',
                                   file_path='schedulerscripts.tar.gz')
print 'SchedulerScripts.tar.gz is uploaded'

blob_service.create_container(container_name = 'processor-node-files')

blob_service.create_blob_from_path(container_name='processor-node-files',
                                   blob_name='processor_bootstrap.sh',
                                   file_path='app/processor_bootstrap.sh')
print 'Processor_bootstrap.sh is uploaded'

blob_service.create_blob_from_path(container_name='processor-node-files',
                                   blob_name='processorscripts.tar.gz',
                                   file_path='processorscripts.tar.gz')
print 'ProcessorScripts.tar.gz is uploaded'

blob_service.create_container(container_name = 'configuration-files')

blob_service.create_blob_from_path(container_name='configuration-files',
                                   blob_name='config.py',
                                   file_path='app/config.py')
print 'config.py is uploaded'

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

print 'AES key decrypted'

# Decode script
aes_cipher = AESCipher(key, iv)
aes_cipher.encrypt_file_save_file(unencrypted_script_filename, encrypted_script_filename)
print unencrypted_script_filename + ' is encrypted and saved to ' + encrypted_script_filename

blob_service.create_blob_from_path(container_name=config.storage_container_name,
                                   blob_name=config.encrypted_scheduler_script_filename,
                                   file_path=encrypted_script_filename)
print encrypted_script_filename + " is uploaded to Azure.Storage"