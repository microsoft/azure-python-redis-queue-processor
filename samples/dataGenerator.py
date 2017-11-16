import base64
import os
from app.config import Config
from app.aescipher import AESCipher
from app.aeskeywrapper import AESKeyWrapper
from app.aeshelper import AESHelper

class DataGenerator(object):

    def __init__(self, config):
        self.config = config
        self.aes_cipher = AESHelper(config).create_aescipher_from_config()

    def generate_data(self, number_of_lines, out_file_path):
        with open(out_file_path, 'wb+') as outFile:
            for line in range(number_of_lines):
                encrypted_record = self.aes_cipher.encrypt(str(line))
                outFile.writelines(base64.b64encode(encrypted_record)+'\n')


if __name__ == "__main__":
    config = Config()
    data_generator = DataGenerator(config)

    data_generator.generate_data(10, "data/data.10.encrypted")
    data_generator.generate_data(100, "data/data.100.encrypted")
    data_generator.generate_data(1000, "data/data.1000.encrypted")
    data_generator.generate_data(10000, "data/data.10000.encrypted")

