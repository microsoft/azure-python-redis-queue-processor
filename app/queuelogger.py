"""
    pip install azure-storage-queue
"""
import sys
import socket
import json
import fileinput
from datetime import datetime
from azure.storage.queue import QueueService, models
from config import Config

class QueueLogger(object):
    """
    This class contains functionality to log stdout to Azure Queue Storage
    """
    def __init__(self):
        """
        Initializes a new instance of the QueueLogger class.

        :param int batch_size: The number of messages to write into a single Azure Storage Queue message.
        """
        self.config = Config()
        self.queue_service = QueueService(account_name =  self.config.storage_account_name,
            sas_token = self.config.logger_queue_sas)
        self.queue_service.encode_function = models.QueueMessageFormat.noencode

    def start_listening(self):
        for line in fileinput.input():
            self.write(line.strip())

    def init_storage(self):
        """
        Initializes storage table & queue, creating it if it doesn't exist.
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        try:
            # will create the logger queue if it doesn't exist
            self.queue_service.create_queue(self.config.logger_queue_name)
            return True
        except Exception as ex:
            self.write_stdout(ex)
            return False


    def flush(self):
        """
        Flush the internal buffer to Storage Queue
        """
        self.put_message_to_queue()

    def write(self, content):
        """
        Buffers string content to be written to Storage Queue

        :param str content: The content to write/buffer
        """
        self.write_stdout(content)
        self.write_queue(content)

    def write_queue(self, content):
        """
        Buffers string content to be written to Storage Queue

        :param str content: The content to write/buffer
        """
        self.queue_service.put_message(self.config.logger_queue_name, content)

    def write_stdout(self, content):
        """
        Buffers string content to be written to Storage Queue

        :param str content: The content to write/buffer
        """
        print(content)


if __name__ == "__main__":
    queuelogger = QueueLogger()
    queuelogger.start_listening()