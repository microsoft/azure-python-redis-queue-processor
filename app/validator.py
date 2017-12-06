import argparse
import logging
import redis
import time
import socket
import sys
import pickle
from datetime import datetime
from rq import Queue, Connection, Worker, get_failed_queue
from jobstatus import JobState
from results import Results
from config import Config
from workloadTracker import WorkloadTracker, WorkloadEventType

# Logger
LOGGER = logging.getLogger(__name__)

class Validator(object):
    """
    Validates the state of all job status records and re-queues any jobs that ran into processing problems.
    """

    def __init__(self, logger, redisHost, redisPort):
        """
        Class constructor.

        :param logger logger: the logger
        :param str redis_host: Redis host where the Redis Q is running
        :param int redis_port: Redis port where the Redis Q is running
        """
        self.logger = logger
        self.config = Config()
        self.redis_host = redisHost
        self.redis_port = redisPort
        self.results = Results(logger, redisHost, redisPort)
        self.workloadTracker = WorkloadTracker(self.logger)

    def check_failed_queue(self, redis_conn):
        """
        Requeue all jobs in the Failed job queue
        """
        with Connection(redis_conn):
            failed_queue = get_failed_queue()

            # TODO: Need to keep track of number of attempts a job is requeued
            for job in failed_queue.get_jobs():
                self.logger.info("Requeued: " + str(job.id))
                failed_queue.requeue(job.id)
    
    def requeue_job(self, job_id):
        """
        Requeues a job for processing

        :param str job_id: Id of the job that needs to be re-processed
        """
        # TODO: Requeue job

    def validate_job_health(self, job_key, redis_conn):
        """
        Validates the health of a job based on the job state and life timespan

        :param str job_key: Key to retrieve job status
        :param object redis_conn: Redis connection object
        """
        # get the job from redis
        jobStatusSerialized = redis_conn.get(job_key)

        if(jobStatusSerialized != None):
            jobStatus = pickle.loads(jobStatusSerialized)
            # check to see if processing started on the job,
            # if the job is still in queued state do nothing and wait for a worker to pick it up to process
            if(jobStatus.job_state == JobState.processing or jobStatus.job_state == JobState.processed):
                # get the lifespan of the job
                lifespan = datetime.utcnow() - jobStatus.created

                # if the lifespan is greater than the config threshold, requeue it
                if(lifespan.seconds > self.config.job_processing_max_time_sec):
                    # requeue job for processing
                    self.requeue_job(jobStatus.job_id)

    def get_active_jobs(self, redis_conn):
        """
        Gets all active jobs from job status collection.

        :param object redis_conn: Redis connection object
        """
        # get all job status keys from redis, if the key exists it is an active job
        keys = redis_conn.keys(self.config.job_status_key_prefix + '*')
        return keys

    def run(self):
        """
        Execute the validator - get all jobs in process and validate their state
        
        :return float perc: returns the percentage of jobs consolidated
        """
        self.logger.info('Validator using redis host: %s:%s', self.redis_host, self.redis_port)

        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port)
        redis_conn = redis.Redis(connection_pool=pool)

        self.logger.info('Starting validator')

        # Wait until redis connection can be established
        while(True):
            try:
                redis_conn.ping()
                self.logger.info("Validator redis connection successful.")
                break
            except redis.exceptions.ConnectionError:
                self.logger.info("Validator - redis isn't running, sleep for 5 seconds.")
                time.sleep(5)

        with Connection(redis_conn):
            activejobs = self.get_active_jobs(redis_conn)
            for jobKey in activejobs:
                # validate job processing health using the job status collection
                self.validate_job_health(jobKey, redis_conn)
            
            # record the number of processed jobs
            total_scheduled_jobs = int(redis_conn.get(self.config.scheduled_jobs_count_redis_key))
            remaining_jobs = total_scheduled_jobs - len(activejobs)
            perc = float(remaining_jobs) / total_scheduled_jobs
            status_msg = "Jobs Successfully Proccessed (%): {0:.2f} ... {1}/{2}".format(perc, remaining_jobs, total_scheduled_jobs)
            self.workloadTracker.write(WorkloadEventType.WORKLOAD_PROCESSING_STATUS, status_msg)
            self.logger.info(status_msg)
        
        # requue jobs in the Failed job queue
        self.check_failed_queue(redis_conn)

        # consolidate any completed results
        self.results.consolidate_results()
        perc = self.results.get_total_jobs_consolidated_status()

        # record the number of consolidated results
        status_msg = "Jobs Consolidated (%): {0:.2f}".format(perc)
        self.workloadTracker.write(WorkloadEventType.WORKLOAD_CONSOLIDATION_STATUS, status_msg)
        self.logger.info(status_msg)

        return perc

def init_logging():
    """
    Initialize the logger
    """
    LOGGER.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s validator.py ' + socket.gethostname() +' %(levelname)-5s %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

def parse_args():
    """
    Parse command line arguments
    """
    config = Config()
    parser = argparse.ArgumentParser(description='Process jobs from the Redis Q')
    parser.add_argument('--redisHost', help='Redis Q host.', default=config.redis_host)
    parser.add_argument('--redisPort', help='Redis Q port.', default=config.redis_port)

    return parser.parse_args()

if __name__ == "__main__":
    # init logging
    init_logging()

    ARGS = parse_args()
    while True:
        LOGGER.info('Running Validator Sample')
        VALIDATOR = Validator(LOGGER, ARGS.redisHost, ARGS.redisPort)
        
        # Run the validator until all jobs are completed
        STATUS = VALIDATOR.run()
        if STATUS == 1.0:
            LOGGER.info('All jobs are completed.')
            break
        
        LOGGER.info('Sleeping for 15 seconds')
        time.sleep(15)