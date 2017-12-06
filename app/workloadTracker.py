"""
Track the workload's progress with specific events published here
"""
import json
from enum import IntEnum
from azure.storage.queue import QueueService, models
from config import Config

class WorkloadEventType(IntEnum):
    """
    Enum for all of the events that need to be tracked to monitor progress and measure perf of the workload
    """
    SCHEDULER_START = 1
    PROCESSOR_START = 2
    PROCESSOR_FORK_START = 3
    WORKLOAD_DONE = 4
    WORKLOAD_PROCESSING_STATUS = 5
    WORKLOAD_CONSOLIDATION_STATUS = 6
    ACTIVE_JOBS = 7
    JOBS_QUEUE_DONE = 8

class WorkloadEvent(object):
    """
    Simple class that contains the workload event information
    """
    def __init__(self):
        self.event_type = None
        self.content = ""

class WorkloadTracker(object):
    """
    Dedicated class to track important events during the running of the workload.
    """
    def __init__(self, logger):
        self.config = Config()
        self.logger = logger
        self.init_storage_services()
    
    def init_storage_services(self):
        """
        Initializes the storage service clients using values from config.py.
        :return: True on success. False on failure.
        :rtype: boolean
        """
        try:
            # creates instances of Azure QueueService
            self.workload_queue_service = QueueService(
                account_name = self.config.storage_account_name, 
                sas_token = self.config.workload_tracker_sas_token)
            self.workload_queue_service.create_queue(self.config.workload_tracker_queue_name)
            self.workload_queue_service.encode_function = models.QueueMessageFormat.noencode

            return True
        except Exception as ex:
            self.logger.Exception(ex, self.init_storage_services.__name__)
            return False

    def write(self, event_type, content=None):
        """
        Write the event to the dedicated workload tracker queue
        """
        # create an event
        evt = WorkloadEvent()
        evt.event_type = int(event_type)
        evt.content = content

        # write serialized event to Azure queue
        serialized_event = json.dumps(evt.__dict__)
        self.workload_queue_service.put_message(self.config.workload_tracker_queue_name, serialized_event)