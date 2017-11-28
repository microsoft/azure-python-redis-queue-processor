"""
    Simple class that reads in the results file, decodes each lines, and prints the results
"""
import base64
import io
import json
from app.aeshelper import AESHelper
from app.config import Config
from azure.storage.blob import BlockBlobService

class Record(object):
    def __init__(self, id, data):
        self.id = id
        self.data = data

def as_payload(dct):
    return Record(dct['id'], dct['data'])

if __name__ == "__main__":
    config = Config()
    aes_helper = AESHelper(config)

    aes_cipher = aes_helper.create_aescipher_from_config()

    storage_service = BlockBlobService(account_name = config.storage_account_name, sas_token = config.results_container_sas_token)

    results = []
    with io.BytesIO() as blobContents:
        storage_service.get_blob_to_stream(config.results_container_name, config.results_consolidated_file, blobContents)
        blobContents.seek(0)

        for result in blobContents.readlines():
            decoded = aes_cipher.decrypt(base64.b64decode(result))
            record = json.loads(decoded, object_hook = as_payload)
            print str(record.id) + " " + str(len(record.data) / 1024) + "KB"
            results.append(record.id)

    results.sort()
    print results
    print len(results)
