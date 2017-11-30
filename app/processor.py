"""
The class contains the Processor that will process each job

module deps:
pip install rq
"""
import argparse
import os
import logging
import redis
import time
import sys
import socket
import multiprocessing
from config import Config
from aescipher import AESCipher
from aeskeywrapper import AESKeyWrapper
from rq import Queue, Connection, Worker

LOGGER = logging.getLogger(__name__)

class Processor(object):
    """
        Processes Redis Q jobs
    """
    def __init__(self, logger, redisHost, redisPort, queues, encryptedAESKeyPath):
        """
        :param logger logger: the logger
        :param str redis_host: Redis host where the Redis Q is running
        :param int redis_port: Redis port where the Redis Q is running
        :param array queues: the queues the worker will listen on
        :param str encryptedAesKeyPath: path to the encrypted AES key file
        """
        self.logger = logger
        self.queues = queues
        self.config = Config()
        self.redis_host = redisHost
        self.redis_port = redisPort
        self.encrypted_aes_key_path = encryptedAESKeyPath

    def _get_aes_key(self):
        """
        Fetches the AES key using the values from the config
        """
        # Decode AES key
        self.logger.info('Decrypting AES Key')
        wrapper = AESKeyWrapper(vault = self.config.azure_keyvault_url,
                                client_id = self.config.service_principal_client_id,
                                secret = self.config.service_principal_secret,
                                tenant = self.config.tenant_id,
                                key_name = self.config.azure_keyvault_key_name,
                                key_version = self.config.azure_keyvault_key_version)

        with open(self.encrypted_aes_key_path, "rb") as aes_key_file:
            wrapped_key = aes_key_file.read()
            keys = wrapper.unwrap_aes_key(wrapped_key)

        return (keys[:self.config.aes_key_length], keys[self.config.aes_key_length:])

    def run(self):
        """
        Execute the job processor - Fetch the AES key and start the Redis Q worker
        """
        self.logger.info('Using redis host: %s:%s', self.redis_host, self.redis_port)

        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port)
        redis_conn = redis.Redis(connection_pool=pool)

        aes_key = self._get_aes_key()

        # TODO: This is how we are passing the AES key to the fork child processes
        # If there is a better way, we should change it.
        os.environ['AES_SECRET'] = aes_key[0]
        os.environ['AES_IV'] = aes_key[1]

        self.logger.info('Starting worker')

        # Wait until redis connection can be established
        while(True):
            try:
                redis_conn.ping()
                self.logger.info("Redis connection successful.")
                break
            except redis.exceptions.ConnectionError:
                self.logger.info("Redis isn't running, sleep for 5 seconds.")
                time.sleep(5)

        with Connection(redis_conn):
            worker = Worker(self.queues)
            worker.work()

def init_logging():
    """
    Initialize the logger
    """
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s processor.py ' + socket.gethostname() +' %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

def parse_args():
    """
    Parse command line arguments
    """
    config = Config()
    parser = argparse.ArgumentParser(description='Process jobs from the Redis Q')
    parser.add_argument('aesKeyFilePath', help='path to the encrypted aes key file.')
    parser.add_argument('--queues', help='Redis Q queues to listen on', default=['high', 'default', 'low'])
    parser.add_argument('--redisHost', help='Redis Q host.', default=config.redis_host)
    parser.add_argument('--redisPort', help='Redis Q port.', default=config.redis_port)

    return parser.parse_args()

def init(args):
    LOGGER.info('Running Processor - Fork')
    PROCESSOR = Processor(LOGGER, args.redisHost, args.redisPort, args.queues, args.aesKeyFilePath)
    PROCESSOR.run()

if __name__ == "__main__":
    # init logging
    init_logging()
    
    LOGGER.info('Running Processor - Main')

    commandLineArgs = parse_args()
    # Fork process
    num_process = multiprocessing.cpu_count()
    LOGGER.info('Lunching {} processing'.format(num_process))
    for i in xrange(num_process):
        p = multiprocessing.Process(target=init, args=(commandLineArgs,))
        p.start()


