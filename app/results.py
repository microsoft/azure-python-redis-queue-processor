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

            # creates instance of Azure QueueService
            self.storage_service_queue = QueueService(account_name = self.config.storage_account_name, sas_token = self.config.job_status_queue_sas_token)
            self.storage_service_queue.encode_function = models.QueueMessageFormat.noencode

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

    def write_result(self, job_id, result):
        """
        Encrypts and writes result to storage

        :param str result: The result to write to storage
        :return: True on success. False on failure.
        :rtype: boolean
        """
        try:
            # encrypt the encoded result and then encode it
            encryptedResult = base64.b64encode(self.aescipher.encrypt(result))

            # write the encrypted and encoded result out to blob storage using the job id as the file name
            self.storage_service.create_blob_from_text(self.config.results_container_name, job_id, encryptedResult)
        except Exception as ex:
            self.log_exception(ex, self.write_result.__name__)
            return False

    def count_results(self):
        """
        Returns a count of results in storage.

        "return: int count: Total count of results in storage.
        """
        try:
            consolidatedResults = self.storage_service_cache.get(self.config.results_consolidated_count_redis_key)
            return consolidatedResults
        except Exception as ex:
            self.log_exception(ex, self.count_results.__name__)
            return False

    def _consolidate_result_blob(self, blob_name):
        """
        Consolidates individual result blob into consolidated result file. Individual result blob is deleted once it
        is added to the consolidated file.

        "param: str blob_name: Name of the individual result blob to consolidate.
        """
        try:
            # read the contents of the blob
            with io.BytesIO() as blobContents:
                self.storage_service.get_blob_to_stream(self.config.results_container_name, blob_name, blobContents)
                blobContents.write(b'\n')
                blobContents.seek(0)

                # append the result blob contents to the consolidated file
                self.logger.info("Appended results blob: " + blob_name)
                self.append_storage_service.append_blob_from_stream(self.config.results_container_name, self.config.results_consolidated_file, blobContents)

            # delete the individual results blob now that it has been added to the consolidated file
            self.logger.info("Deleting results blob: " + blob_name + " from container: " + self.config.results_container_name)
            self.storage_service.delete_blob(self.config.results_container_name, blob_name)

            # update the consolidated results count in Redis, we do this per iteration of the loop so if
            # this process / VM fails during consolidation we still have an accurate count
            totalConsolidatedResults = self.storage_service_cache.get(self.config.results_consolidated_count_redis_key)
            if(totalConsolidatedResults == None):
                totalConsolidatedResults = 0

            # change the redis total results value to an int
            total = int(totalConsolidatedResults)
            total += 1
            self.logger.info("Results consolidated: " + str(total))
            self.storage_service_cache.set(self.config.results_consolidated_count_redis_key, total)

        except Exception as ex:
            self.log_exception(ex, self.consolidate_results.__name__ + " - Error consolidating result blob.")

    def consolidate_results(self):
        """
        Consolidates all individual result files into single result file in storage. Blobs are deleted once they
        are added to the consolidated file.

        "return: int count: Total count of results consolidated in result file.
        """
        # create a counter to track the total results consolidated by this function
        resultsConsolidated = 0

        try:
            # ensure the consolidated append blob exists
            if(self.append_storage_service.exists(self.config.results_container_name, blob_name=self.config.results_consolidated_file) == False):
                self.append_storage_service.create_blob(self.config.results_container_name, self.config.results_consolidated_file)

            # boolean to track whether or not we found any blobs to consolidate
            blobsConsolidated = True

            # keep looping as long as we've found results to consolidate
            while(blobsConsolidated):
                blobsConsolidated = False
                # get a list of result blobs to consolidate
                resultBlobs = self.storage_service.list_blobs(self.config.results_container_name)

                # iterate through the blobs in the container
                for blob in resultBlobs:
                    # make sure the blob we got back from the container isn't the consolidated blob
                    if(blob.name != self.config.results_consolidated_file):
                        # update the results consolidated in this function counter
                        resultsConsolidated += 1

                        # consolidate the result blob
                        self._consolidate_result_blob(blob.name)

                        # update the boolean so we know we should check for more blobs to consolidate after the
                        # blobs listed in the current generator are all consolidated
                        blobsConsolidated = True

            # write the count of results we consolidated out to queue to provide status
            self.storage_service_queue.put_message(self.config.job_status_queue_name, str(resultsConsolidated) + " results consolidated.")

            return resultsConsolidated

        except Exception as ex:
            self.log_exception(ex, self.consolidate_results.__name__)
            return resultsConsolidated