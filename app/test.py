import logging
import time
from jobstatus import JobStatus, JobState
from metricslogger import MetricsLogger

logger = logging.getLogger(__name__)

def initLogging():
    logger.setLevel(logging.DEBUG)
    # setup a console logger by default
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

if __name__ == "__main__":
    initLogging()

    # job status tests
    jobName = "TestJob"
    jobId = "1111"
    js = JobStatus(logger)
    js.add_job_status(jobName, jobId, JobState.none)
    time.sleep(5)
    js.update_job_status(jobId, JobState.queued)
    time.sleep(5)
    js.update_job_status(jobId, JobState.processing)
    time.sleep(5)
    js.update_job_status(jobId, JobState.processed)
    time.sleep(5)
    js.update_job_status(jobId, JobState.failed, 'crazy error')
    
    # metrics logger test
    ml = MetricsLogger(logger)
    ml.capture_vm_metrics()