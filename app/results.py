import base64
import redis
import time
import azure.common
import io
from datetime import datetime
from azure.storage.blob import BlockBlobService, AppendBlobService
from azure.storage.queue import QueueService, models
from config import Config
from aescipher import AESCipher
from aeshelper import AESHelper

class Results(object):
    """
    Handles interacting with encrypted results in blob storage.
    """
    def __init__(self, logger, redisHost, redisPort):
        """
        Initializes a new instance of the JobStatus class.

        :param logger logger: The logger instance to use for logging
        :param str redis_host: Redis host where the Redis Q is running
        :param int redis_port: Redis port where the Redis Q is running
        """
        self.logger = logger
        self.config = Config()
        self.redis_host = redisHost
        self.redis_port = redisPort
        # create an instance of AESCipher to use for encryption
        aesHelper = AESHelper(self.config)
        self.aescipher = aesHelper.create_aescipher_from_config()
        if(self.init_storage_services() is False):
            raise Exception("Errors occurred instantiating results storage service.")

    def init_storage_services(self):
        """
        Initializes the storage service clients using values from config.py.
        :return: True on success. False on failure.
        :rtype: boolean
        """
        try:
            # creates instance of BlockBlobService and AppendBlobService to use for completed results storage
            self.storage_service = BlockBlobService(account_name = self.config.storage_account_name, sas_token = self.config.results_container_sas_token)
            self.append_storage_service = AppendBlobService(account_name = self.config.storage_account_name, sas_token = self.config.results_container_sas_token)
            self.storage_service.create_container(self.config.results_container_name)

            # creates instances of Azure QueueService
            self.job_status_queue_service = QueueService(account_name = self.config.storage_account_name, sas_token = self.config.job_status_queue_sas_token)
            self.job_status_queue_service.encode_function = models.QueueMessageFormat.noencode
            self.results_queue_service = QueueService(account_name = self.config.storage_account_name, sas_token = self.config.results_queue_sas_token)
            self.results_queue_service.create_queue(self.config.results_container_name)
            self.results_queue_service.encode_function = models.QueueMessageFormat.noencode

            # creates instance of Redis client to use for job status storage
            pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port)
            self.storage_service_cache = redis.Redis(connection_pool=pool)

            return True
        except Exception as ex:
            self.log_exception(ex, self.init_storage_services.__name__)
            return False

    def log_exception(self, exception, functionName):
        """
        Logs an exception to the logger instance for this class.

        :param Exception exception: The exception thrown.
        :param str functionName: Name of the function where the exception occurred.
        """
        self.logger.debug("Exception occurred in: " + functionName)
        self.logger.debug(type(exception))
        self.logger.debug(exception)

    def write_result(self, result):
        """
        Encrypts and writes result to queue

        :param str result: The result to write to queue
        :return: True on success. False on failure.
        :rtype: boolean
        """
        try:
            # encrypt the encoded result and then encode it
            encryptedResult = base64.b64encode(self.aescipher.encrypt(result))

            # put the encoded result into the azure queue for future consolidation
            self.results_queue_service.put_message(self.config.results_queue_name, encryptedResult)

            return True
        except Exception as ex:
            self.log_exception(ex, self.write_result.__name__)
            return False

    def count_consolidated_results(self):
        """
        Returns a count of results that were consolidated.

        "return: int count: Total count of results that were consolidated.
        """
        try:
            consolidatedResults = self.storage_service_cache.get(self.config.results_consolidated_count_redis_key)
            return consolidatedResults
        except Exception as ex:
            self.log_exception(ex, self.count_consolidated_results.__name__)
            return False

        except Exception as ex:
            self.log_exception(ex, self.consolidate_results.__name__ + " - Error consolidating result blob.")

    def consolidate_results(self):
        """
        Consolidates all individual result files into single result file in storage. Blobs are deleted once they
        are added to the consolidated file.

        "return: int count: Total count of results consolidated in result file.
        """
        try:
            # ensure the consolidated append blob exists
            if not self.append_storage_service.exists(self.config.results_container_name, blob_name=self.config.results_consolidated_file):
                self.append_storage_service.create_blob(self.config.results_container_name, self.config.results_consolidated_file)

            result_messages = []
            with io.BytesIO() as consolidated_result:
                while len(result_messages) < self.config.result_consolidation_size:
                    messages = self.results_queue_service.get_messages(self.config.results_queue_name, min(self.config.result_consolidation_size, 32))
                    
                    # If the queue is empty, stop and consolidate
                    if not messages:
                        break

                    # add the message to the memory stream
                    for msg in messages:
                        consolidated_result.write(msg.content+"\n")
                        result_messages.append(msg)
            
                # append the results to the consolidated file
                consolidated_result.seek(0)
                self.append_storage_service.append_blob_from_stream(self.config.results_container_name, self.config.results_consolidated_file, consolidated_result)

            # remove all of the messages from the queue
            for msg in result_messages:
                self.results_queue_service.delete_message(self.config.results_queue_name, msg.id, msg.pop_receipt)
            self.storage_service_cache.incrby(self.config.results_consolidated_count_redis_key, len(result_messages))

            # write the count of results we consolidated out to queue to provide status
            self.job_status_queue_service.put_message(self.config.job_status_queue_name, str(len(result_messages)) + " results consolidated.")

            return len(result_messages)

        except Exception as ex:
            self.log_exception(ex, self.consolidate_results.__name__)
            return len(result_messages)

    def get_total_jobs_consolidated_status(self):
        """
        Write out the the current state of the workload; the percentage of jobs that are completed and consolidated
        "return: float status: percentage of completed jobs
        """
        # log out total job status
        total_scheduled_jobs = self.storage_service_cache.get(self.config.scheduled_jobs_count_redis_key)
        total_consolidated_results = self.storage_service_cache.get(self.config.results_consolidated_count_redis_key)
        
        if total_consolidated_results is None:
            total_consolidated_results = "0"

        status_message = "Total: "+ total_consolidated_results + "/" + total_scheduled_jobs + " jobs have been successfully processed and consolidated."
        self.logger.info(status_message)
        self.job_status_queue_service.put_message(self.config.job_status_queue_name, status_message)

        return float(total_consolidated_results) / int(total_scheduled_jobs)