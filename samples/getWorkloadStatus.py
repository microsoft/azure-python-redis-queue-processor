"""
This script will pull messages from the Job Status Queue and print out the messages that show total status.
"""

from app.config import Config
from azure.storage.queue import QueueService
import sys
import time

LOG_EVENT_MSGS = [
    "Running Scheduler - Main",
    "Running Processor - Main",
    "Running Processor - Fork",
    "Jobs Completed (%): ",
    "All jobs are completed."
]

RESULTS_EVENT_MSG = "Total: "

class Event(object):

    def __init__(self, event_name, time_stamp, contents):
        self.event_name = event_name
        self.time_stamp = time_stamp
        self.contents = contents

if __name__ == "__main__":
    config = Config()

    job_queue_service = QueueService(account_name=config.storage_account_name,
                sas_token=config.job_status_queue_sas_token)
    
    log_queue_service = QueueService(account_name=config.storage_account_name,
                sas_token=config.logger_queue_sas)

    while True:
        messages = log_queue_service.get_messages(config.logger_queue_name, 32)
        if len(messages) == 0:
            break

        for msg in messages:
            for event in LOG_EVENT_MSGS:
                if event in str(msg.content):
                    print str(msg.insertion_time) + " " + msg.content
                

            #job_queue_service.delete_message(config.logger_queue_name, msg.id, msg.pop_receipt)

    while True:
        messages = job_queue_service.get_messages(config.job_status_queue_name, 32)
        if len(messages) == 0:
            break

        for msg in messages:
            if str(msg.content).startswith(RESULTS_EVENT_MSG):
                print str(msg.insertion_time) + " " + msg.content

            #job_queue_service.delete_message(config.job_status_queue_name, msg.id, msg.pop_receipt)


        
        
