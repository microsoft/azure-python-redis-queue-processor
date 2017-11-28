import base64
import json
import os
from app.config import Config
from app.aescipher import AESCipher
from app.aeskeywrapper import AESKeyWrapper
from app.aeshelper import AESHelper

class Record(object):
    id = -1
    data = ""

    def __init__(self, size):
        self.id = id
        self._initData(size)

    def _initData(self, size):
        for i in range(size * 1024):
            self.data += "A"

class DataGenerator(object):

    def __init__(self, config):
        self.config = config
        self.aes_cipher = AESHelper(config).create_aescipher_from_config()

    def generate_data(self, size_of_record_kb, number_of_records, out_file_path):

        record = Record(size_of_record_kb)

        with open(out_file_path, 'wb+') as out_file:
            for recordId in range(number_of_records):
                record.id = recordId              
                encrypted_record = self.aes_cipher.encrypt(json.dumps(record.__dict__))
                out_file.writelines(base64.b64encode(encrypted_record)+'\n')


if __name__ == "__main__":
    config = Config()
    data_generator = DataGenerator(config)

    data_generator.generate_data(1, 10, "data/data.10.encrypted")
    data_generator.generate_data(1, 100, "data/data.100.encrypted")
    data_generator.generate_data(1, 1000, "data/data.1000.encrypted")
    data_generator.generate_data(1, 10000, "data/data.10000.encrypted")

