import pickle
from datetime import datetime
from enum import IntEnum
from azure.cosmosdb.table import TableService, Entity
from azure.storage.queue import QueueService, models
from config import Config

class JobState(IntEnum):
    none = 0
    queued = 1
    processing = 2
    processed = 3
    done = 4
    failed = 5

class JobStatus(object):
    """
    Class for managing job status records.
    """
    def __init__(self, logger):
        """
        Initializes a new instance of the JobStatus class.

        :param logger logger: The logger instance to use for logging.
        """
        self.logger = logger
        self.config = Config()
        if(self.init_storage_services() is False):
            raise Exception("Errors occured instantiating job status storage service.")

        if(self.init_storage() is False):
            raise Exception("Errors occured validating job status table exists.")

    def init_storage_services(self):
        """
        Initializes the storage service clients using values from config.py.
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        try:
            # creates instance of TableService to use for job status storage
            self.storage_service_table = TableService(account_name = self.config.job_status_storage, sas_token = self.config.job_status_sas_token)
            
            # creates instance of QueueService to use for completed job status storage
            self.storage_service_queue = QueueService(account_name = self.config.job_status_storage, sas_token = self.config.job_status_sas_token)
            
            # set the encode function for objects stored as queue message to noencode, serialization will be handled as a string by pickle
            # http://azure-storage.readthedocs.io/en/latest/ref/azure.storage.queue.queueservice.html
            # http://azure-storage.readthedocs.io/en/latest/_modules/azure/storage/queue/models.html
            self.storage_service_queue.encode_function = models.QueueMessageFormat.noencode
            
            return True
        except Exception as ex:
            self.log_exception(ex, self.init_storage_services.__name__)
            return False

    def init_storage(self):
        """
        Initializes storage table & queue, creating it if it doesn't exist.
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        try:
            # will create job status table and queue if either doesn't exist
            self.storage_service_table.create_table(self.config.job_status_storage)
            self.storage_service_queue.create_queue(self.config.job_status_storage)
            return True
        except Exception as ex:
            self.log_exception(ex, self.init_storage.__name__)
            return False

    def log_exception(self, exception, functionName):
        """
        Logs an exception to the logger instance for this class.

        :param Exeption exception: The exception thrown.
        :param str functionName: Name of the function where the exception occurred.
        """
        self.logger.debug("Exception occurred in: " + functionName)
        self.logger.debug(type(exception))
        self.logger.debug(exception)

    def add_job_status(self, jobName, jobId, jobState):
        """
        Adds a new job status record.

        :param str jobName: The name of the job, this will be used as the partition key for the table.
        :param str jobId: Id for the job.
        :param JobState jobState: Enum for the current job state.
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        record = Entity()
        record.PartitionKey = jobName
        record.RowKey = jobId
        record.Created = datetime.utcnow()
        record.State = int(jobState)
        try:
            self.storage_service_table.insert_entity(self.config.job_status_storage, record)
            return True
        except Exception as ex:
            self.log_exception(ex, self.add_job_status.__name__)
            return False

    def get_job_status(self, jobName, jobId):
        """
        Gets a job status record from storage.

        :param str jobName: The name of the job, this will be used as the partition key for the table.
        :param str jobId: Id for the job.
        :return: Entity record on success. None on failure.
        :rtype: Entity or None
        """
        try:
            record = self.storage_service_table.get_entity(self.config.job_status_storage, jobName, jobId)
            return record
        except Exception as ex:
            self.log_exception(ex, self.get_job_status.__name__)
            return None

    def update_job_status(self, jobName, jobId, jobState, error = None):
        """
        Updates a job status record.

        :param str jobName: The name of the job, this will be used as the partition key for the table.
        :param str jobId: Id for the job.
        :param JobState jobState: Enum for the current job state.
        :param error: Optional parameter to provide error details for failed state.
        :type error: str or None
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        record = self.get_job_status(jobName, jobId)
        record.PartitionKey = jobName
        record.RowKey = jobId
        record.LastUpdated = datetime.utcnow()
        record.State = int(jobState)
        if(error is not None):
            record.LastError = error
        try:
            # write the job status record out to table storage
            self.storage_service_table.update_entity(self.config.job_status_storage, record)

            # if the job is complete or failed, write it out to the queue
            if(jobState is JobState.done or jobState is JobState.failed):
                self.queue_job_status(record)

            return True
        except Exception as ex:
            self.log_exception(ex, self.update_job_status.__name__)
            return False

    def queue_job_status(self, jobStatus):
        """
        Queues at job status record

        :param object jobStatus: The job status record to store in the queue message.
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        try:
            jobStatusSerialized = pickle.dumps(jobStatus)
            self.storage_service_queue.put_message(self.config.job_status_storage, jobStatusSerialized)
            return True
        except Exception as ex:
            self.log_exception(ex, self.queue_job_status.__name__)
            return False