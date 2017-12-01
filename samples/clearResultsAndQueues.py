"""
This script will clear all of the queues and the blob container that holds the results from a workload.
This is mainly for testing or re-running a workload against an existing enviroment's configuration.
"""
import time
import azure.common
from azure.storage.blob import BlockBlobService
from azure.storage.queue import QueueService, models
from app.config import Config

if __name__ == "__main__":
    config = Config()

    queues = [ 
        (config.job_status_queue_name, config.job_status_queue_sas_token),
        (config.logger_queue_name, config.logger_queue_sas), 
        (config.metrics_queue_name, config.metrics_sas_token)
    ]

    print "Clearing all queues"
    for queue in queues:
        storage_service_queue = QueueService(account_name = config.storage_account_name, sas_token = queue[1])
        storage_service_queue.clear_messages(queue[0])
        print "\t" + queue[0] + " cleared."

    storage_service = BlockBlobService(account_name = config.storage_account_name, sas_token = config.results_container_sas_token)
    
    print "Deleting container: " + config.results_container_name
    storage_service.delete_container(config.results_container_name)

    print "\tAttempting to recreate the container: " + config.results_container_name
    while True:
        try:
            succ = storage_service.create_container(config.results_container_name, fail_on_exist=True)
            if succ:
                print "Successfully recreated container: " + config.results_container_name
                break 
        except azure.common.AzureConflictHttpError:
            print "\tNeed to wait for container to be deleted... sleeping for 10 seconds."
            time.sleep(10)
