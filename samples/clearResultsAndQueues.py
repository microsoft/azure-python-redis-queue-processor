from azure.storage.blob import BlockBlobService
from azure.storage.queue import QueueService, models
from app.config import Config

config = Config()

queues = [ 
    (config.job_status_queue_name, config.job_status_queue_sas_token),
    (config.logger_queue_name, config.logger_queue_sas), 
    (config.metrics_queue_name, config.metrics_sas_token)
]

for queue in queues:
    storage_service_queue = QueueService(account_name = config.storage_account_name, sas_token = queue[1])
    storage_service_queue.clear_messages(queue[0])

storage_service = BlockBlobService(account_name = config.storage_account_name, sas_token = config.results_container_sas_token)
storage_service.delete_container(config.results_container_name)
storage_service.create_container(config.results_container_name)