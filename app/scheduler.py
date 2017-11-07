"""
Scheduler.py will read a data file, format it, and then enqueue jobs for each record into Redis Q

module deps:
pip install rq
"""
import argparse
import logging
import redis
import time
import sys
import socket
from datetime import datetime
from config import Config
from functions import processing_job
from rq import Queue, Connection
from aescipher import AESCipher
from aeskeywrapper import AESKeyWrapper
from jobstatus import JobStatus, JobState
from queuelogger import QueueLogger

QUEUELOGGER = QueueLogger(1)
sys.stdout = QUEUELOGGER
sys.stderr = QUEUELOGGER
LOGGER = logging.getLogger(__name__)

class Scheduler(object):
    """
    Scheduler class enqueues jobs to Redis Q
    """
    def __init__(self, logger, redis_host, redis_port):
        """
        :param logger logger: logger
        :param str redis_host: Redis host where the Redis Q is running
        :param int redis_port: Redis port where the Redis Q is running
        """
        self.config = Config()
        self.logger = logger
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.jobstatus = JobStatus(logger, redis_host, redis_port)

    def format_record(self, record):
        """
        TODO: Implement any formatting needed to transform the data before enqueueing

        :param object record: an encrypted record from the data file
        :return: formatted record
        """
        return record.rstrip('\n')

    def run(self, data_file_path):
        """
        Run the queueing job

        :param str ata_file_path: path to the file with the data to be processed
        :return: jobs that were queued
        """
        self.logger.info('processing data file:, %s', data_file_path)
        self.logger.info('Using redis host: %s:%s', self.redis_host, self.redis_port)

        # get a redis connection
        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port)
        redis_conn = redis.Redis(connection_pool=pool)

        # Wait until redis connection can be established
        while(True):
            try:
                redis_conn.ping()
                self.logger.info("Redis connection successful.")
                break
            except redis.exceptions.ConnectionError:
                self.logger.info("Redis isn't running, sleep for 5 seconds.")
                time.sleep(5)

        # read in the file and queue up jobs
        count = 0
        jobs = []
        jobname = str(datetime.utcnow())
        with open(data_file_path, 'r') as data_file:
            with Connection(redis_conn):
                queue = Queue()
                for record in data_file:
                    job = queue.enqueue(processing_job, self.format_record(record), self.jobstatus)
                    self.jobstatus.add_job_status(jobname, job.id, JobState.queued)
                    
                    count += 1
                    jobs.append(job)

        self.logger.info('%d jobs queued', count)

        return jobs

def init_logging():
    """
    Initialize the logger
    """
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(QUEUELOGGER)
    formatter = logging.Formatter(socket.gethostname() + ' %(asctime)s %(name)-20s %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

def parse_args():
    """
    Parse command line arguments
    """
    config = Config()
    parser = argparse.ArgumentParser(description='Enqueue jobs to Redis Q')
    parser.add_argument('dataFilePath', help='path to the data file.')
    parser.add_argument('--redisHost', help='Redis Q host.', default=config.redis_host)
    parser.add_argument('--redisPort', help='Redis Q port.', default=config.redis_port)

    return parser.parse_args()

if __name__ == "__main__":
    # init logging
    init_logging()

    ARGS = parse_args()

    LOGGER.info('Running Scheduler Sample')
    # start program
    SCHEDULER = Scheduler(LOGGER, ARGS.redisHost, ARGS.redisPort)
    JOBS = SCHEDULER.run(ARGS.dataFilePath)

    time.sleep(3)
    for job in JOBS:
        jobinfo = {
            'id': job.id,
            'status' : job.status,
            'result' : job.result
        }
        print(jobinfo)