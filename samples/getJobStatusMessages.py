"""
This script will pull messages from the Job Status Queue and print out the messages that show total status.
"""

from app.config import Config
from azure.storage.queue import QueueService
import sys
import time


if __name__ == "__main__":
    config = Config()

    queue_service = QueueService(account_name = config.storage_account_name,
                sas_token = config.job_status_queue_sas_token)

    while True:
        messages = queue_service.get_messages(config.job_status_queue_name, 32)
        for msg in messages:

            if str(msg.content).startswith("Total: "):
                print str(msg.insertion_time) + " " + msg.content

            queue_service.delete_message(config.job_status_queue_name, msg.id, msg.pop_receipt)


        
        
