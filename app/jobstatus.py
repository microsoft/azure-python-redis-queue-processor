import pickle
import redis
from datetime import datetime
from enum import IntEnum
from azure.storage.queue import QueueService, models
from config import Config

class JobState(IntEnum):
    none = 0
    queued = 1
    processing = 2
    processed = 3
    done = 4
    failed = 5

class JobStatusRecord(object):
    """
    Custom object to track a single job's status
    """
    def __init__(self):
        """
        Initializes a new instance of the JobStatusRecord custom object.
        """
        self.job_name = ""
        self.job_id = ""
        self.job_state = JobState.none
        self.created = None
        self.last_updated = None
        self.last_error = None
        
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
            # creates instance of Redis client to use for job status storage
            pool = redis.ConnectionPool(host=self.config.redis_host, port=self.config.redis_port)
            self.storage_service_cache = redis.Redis(connection_pool=pool)
            
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
            # will create job status queue if it doesn't exist
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
        record = JobStatusRecord()
        record.job_name = jobName
        record.job_id = jobId
        record.created = datetime.utcnow()
        record.job_state = int(jobState)
        try:
            # serialize the JobStatusRecord
            jobStatusSerialized = pickle.dumps(record)

            # write the serialized record out to Redis
            self.storage_service_cache.set(self.config.job_status_key_pattern + jobId, jobStatusSerialized)
            self.logger.info('queued: ' + jobId)
            return True
        except Exception as ex:
            self.log_exception(ex, self.add_job_status.__name__)
            return False

    def get_job_status(self, jobId):
        """
        Gets a job status record from storage.

        :param str jobId: Id for the job.
        :return: JobStatusRecord record on success. None on failure.
        :rtype: JobStatusRecord or None
        """
        try:
            # get the serialized job status record from Redis
            serializedRecord = self.storage_service_cache.get(self.config.job_status_key_pattern + jobId)

            # deserialize the record and return the JobStatusRecord object
            return pickle.loads(serializedRecord)
        except Exception as ex:
            self.log_exception(ex, self.get_job_status.__name__)
            return None

    def update_job_status(self, jobId, jobState, error = None):
        """
        Updates a job status record.

        :param str jobId: Id for the job.
        :param JobState jobState: Enum for the current job state.
        :param error: Optional parameter to provide error details for failed state.
        :type error: str or None
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        record = self.get_job_status(jobId)
        record.job_id = jobId
        record.last_updated = datetime.utcnow()
        record.job_state = int(jobState)
        if(error is not None):
            record.last_error = error
        try:
            # serialize the JobStatusRecord
            jobStatusSerialized = pickle.dumps(record)

            # write the job status record out to storage
            self.storage_service_cache.set(self.config.job_status_key_pattern + jobId, jobStatusSerialized)

            # if the job is complete or failed, write it out to the queue and remove it from the job status collection
            if(jobState is JobState.done or jobState is JobState.failed):
                self.queue_job_status(record)
                self.storage_service_cache.delete(self.config.job_status_key_pattern + jobId)

            return True
        except Exception as ex:
            self.log_exception(ex, self.update_job_status.__name__)
            return False

    def queue_job_status(self, jobStatusRecord):
        """
        Queues at job status record

        :param object jobStatus: The job status record to store in the queue message.
        :return: True on succeess. False on failure.
        :rtype: boolean
        """
        try:
            jobStatusRecordSerialized = pickle.dumps(jobStatusRecord)
            self.storage_service_queue.put_message(self.config.job_status_storage, jobStatusRecordSerialized)
            return True
        except Exception as ex:
            self.log_exception(ex, self.queue_job_status.__name__)
            return False