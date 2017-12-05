"""
    config.py only contains the configuration class
"""
import os
import json

class Config(object):
    """
    This class contains configuration parameters for all applications
    """
    def __init__(self, config_file="config/config.json"):
        with open(config_file, "rt") as conf:
            self.__dict__ = json.loads(conf.read())

    subscription_id = ""
    tenant_id = ""
    service_principal_client_id = ""
    service_principal_secret = ""
    redis_port = 6379,
    redis_host = "localhost"
    number_of_records = 100
    result_consolidation_size = 10
    size_of_record_kb = 1
    job_processing_max_time_sec = 60,
    azure_keyvault_url = ""
    azure_keyvault_key_name = ""
    azure_keyvault_key_version = ""
    aes_key_length = 32,
    storage_account_name = ""
    unencrypted_scheduler_script_filename = ""
    encrypted_scheduler_script_filename = ""
    storage_container_name = ""
    encrypted_data_filename = ""
    encrypted_aes_key_filename = ""
    encrypted_files_folder = ""
    app_code_folder = ""
    encrypted_files_sas_token = ""
    metrics_queue_name = "metrics"
    metrics_sas_token = ""
    metrics_vm_resource_group = ""
    logger_queue_name = "logger"
    logger_queue_sas = ""
    scheduled_jobs_count_redis_key = "totalScheduledJobsCount"
    results_queue_name = "results"
    results_queue_sas_token = ""
    results_container_name = "results"
    results_consolidated_file = ""
    results_consolidated_count_redis_key = "consolidatedResultsCount"
    results_container_sas_token = ""
    job_status_key_prefix = "task-status-"
    job_status_queue_name = ""
    job_status_queue_sas_token = ""

