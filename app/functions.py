"""
  Functions that will be executed by the jobs
"""
import os
import logging
from datetime import datetime
from aescipher import AESCipher
from jobstatus import JobStatus
from jobstatus import JobState
from rq import get_current_job
LOGGER = logging.getLogger(__name__)

def init_logging():
    """
    Initialize the logger
    """
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

init_logging()
jobstatus = JobStatus(LOGGER)    

def multiply_by_two(x):
    """
    Simple test function
    """
    if x % 5 == 0:
        raise Exception('Went wrong')

    return x * 2

def _create_aes_cipher():
    """
    Get the environment variables set for the AES Key from the job processor
    and construct the AESCipher
    :return: an AESCipher created from the AES key and IV set by the parent process
    """
    return AESCipher(os.environ['AES_SECRET'], os.environ['AES_IV'])

def processing_job(encryptedRecord):
    """
    This will decrypt the data and perform some task
    :param object encryptedRecord: This is the encrypted record to be processed
    :return: returns result of the job
    """
    job = get_current_job()
    aes_cipher = _create_aes_cipher()
    record = int(aes_cipher.decrypt(encryptedRecord))
    jobstatus.update_job_status(job.id, JobState.done)
    return record * 2
