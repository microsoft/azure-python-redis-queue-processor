"""
    pip install azure-storage-queue
"""
import sys
import socket
import json
from datetime import datetime
from azure.storage.queue import QueueService, models
from config import Config

class QueueLogger(object):
    """
    This class contains functionality to log stdout to Azure Queue Storage
    """
    def __init__(self, batch_size):
        """
        Initializes a new instance of the QueueLogger class.

        :param int batch_size: The number of messages to write into a single Azure Storage Queue message.
        """
        self.terminal = sys.stdout
        self.config = Config()
        self.batch_size = batch_size
        self.queue_service = QueueService(account_name =  self.config.logger_storage_account_name,
            sas_token = self.config.logger_queue_sas)
        self.queue_service.encode_function = models.QueueMessageFormat.noencode
        self.messages_to_write = []

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
        self.terminal.write(content)
<<<<<<< HEAD
        if(content == '\n' or content == ''):
            return

        self.messages_to_write.append(content)
        if(len(self.messages_to_write) >= self.batch_size):
            self.put_message_to_queue()

=======
        if(content == '\n' or content == ''): 
            return
        
        self.messages_to_write.append(content)        
        if(len(self.messages_to_write) >= self.batch_size):
            self.put_message_to_queue()
        
>>>>>>> 1f28c09... Added support for logging to queue storage
    def put_message_to_queue(self):
        """
        Adds a new Storage Queue message to the back of the message queue.
        """
<<<<<<< HEAD
        if(self.messages_to_write):
            json_content = json.dumps(self.messages_to_write,sort_keys=True,indent=4, separators=(',', ': '))
            self.queue_service.put_message(self.config.logger_queue_name, content = json_content)
            del self.messages_to_write[:]
=======
        json_content = json.dumps(self.messages_to_write,sort_keys=True,indent=4, separators=(',', ': '))
        self.queue_service.put_message(self.config.logger_queue_name, content = json_content)
        del self.messages_to_write[:]
>>>>>>> 1f28c09... Added support for logging to queue storage
