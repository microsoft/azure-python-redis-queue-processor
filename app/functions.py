"""
  Functions that will be executed by the jobs
"""
import base64
import os
import logging
import socket
import sys
from datetime import datetime
from aescipher import AESCipher
from jobstatus import JobStatus, JobState
from results import Results
from rq import get_current_job

LOGGER = logging.getLogger(__name__)

def init_logging():
    """
    Initialize the logger
    """
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s functions.py ' + socket.gethostname() +' %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

init_logging()

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

def processing_job(encryptedRecord, redisHost, redisPort):
    """
    This will decrypt the data and perform some task
    :param object encryptedRecord: This is the encrypted record to be processed
    """
    # get the current job to process and create the aes cipher
    job = get_current_job()
    aes_cipher = _create_aes_cipher()

    # decrypt the data to be processed
    record = aes_cipher.decrypt(base64.b64decode(encryptedRecord))

    # similuate CPU intensive process for 1 second
    start = datetime.utcnow()
    while True:
        runtime = datetime.utcnow() - start
        if(runtime.seconds > 1):
            break

    # write out the results
    results = Results(LOGGER, redisHost, redisPort)
    results.write_result(job.id, record)

    # update the job status record
    jobstatus = JobStatus(LOGGER, redisHost, redisPort)
    jobstatus.update_job_status(job.id, JobState.done)
