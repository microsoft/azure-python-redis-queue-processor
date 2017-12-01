"""
This script will pull messages from the Job Status Queue and print out the messages that show total status.
"""

from app.config import Config
from azure.storage.queue import QueueService
import sys
import time

SCHEDULER_START = "Running Scheduler - Main"
PROCESSOR_START = "Running Processor - Main"
PROCESSOR_FORK_START = "Running Processor - Fork"
JOB_STATUS = "Jobs Completed (%):"
WORKLOAD_DONE_MSG = "All jobs are completed."

class WorkloadEvent(object):
    def __init__(self, event_name, time_stamp, contents):
        self.event_name = event_name
        self.time_stamp = time_stamp
        self.contents = contents

class Workload(object):
    def __init__(self, config):
        self.workloadCompleteEvent = None
        self.schedulerStartEvent = None
        self.config = config
        self.log_queue_service = QueueService(account_name=self.config.storage_account_name,
                sas_token=self.config.logger_queue_sas)
        self.processorEvents = []
        self.processorForkEvents = []
        self.jobCompletionEvents = []

    def get_events(self):
        print "Getting Relevant Workload Events"
        while True:
            messages = self.log_queue_service.get_messages(self.config.logger_queue_name, 32)
            for msg in messages:
                content = str(msg.content)
                event = None    

                # Workload Completed
                if WORKLOAD_DONE_MSG in content:
                    event = WorkloadEvent(WORKLOAD_DONE_MSG, msg.insertion_time, msg.content)
                    self.workloadCompleteEvent = event

                # Scheduler - Main Start
                if SCHEDULER_START in content:
                    event = WorkloadEvent(SCHEDULER_START, msg.insertion_time, msg.content)
                    self.schedulerStartEvent = event
                
                # Processor - Main Start
                if PROCESSOR_START in content:
                    event = WorkloadEvent(PROCESSOR_START, msg.insertion_time, msg.content)
                    self.processorEvents.append(event)
                
                # Processor - Fork Start
                if PROCESSOR_FORK_START in content:
                    event = WorkloadEvent(PROCESSOR_FORK_START, msg.insertion_time, msg.content)
                    self.processorForkEvents.append(event)
                
                # Job Completion Status
                if JOB_STATUS in content:
                    event = WorkloadEvent(PROCESSOR_FORK_START, msg.insertion_time, msg.content)
                    self.jobCompletionEvents.append(event)

                if event is not None:
                    print str(event.time_stamp) + " " + event.contents     

            # Stop when the workload is completed    
            if self.workloadCompleteEvent is not None and self.schedulerStartEvent is not None:
                break

            # Sleeping to avoid spamming
            if not messages: 
                time.sleep(30)
    
    def print_summary(self):
        print "\nSummary: "
        print "Scheduler Started: " + str(self.schedulerStartEvent.time_stamp)
        print "Workload Completed: " + str(self.workloadCompleteEvent.time_stamp)
        print "Number of Processors: " + str(len(self.processorEvents))
        self.processorEvents.sort(key=lambda evt: evt.time_stamp)
        print "\tFirst Processor Up: " + str(self.processorEvents[0].time_stamp)
        print "\tLast Processor Up: " + str(self.processorEvents[-1].time_stamp)
        print "\tNumber of Forked Processors Instances: " + str(len(self.processorForkEvents))
        elapseWorkloadTime = divmod((self.workloadCompleteEvent.time_stamp - self.schedulerStartEvent.time_stamp).total_seconds(), 60)
        print "Workload Elapsed Time: " + str(elapseWorkloadTime[0]) + " mins, " + str(elapseWorkloadTime[1]) + " secs"

if __name__ == "__main__":
    WORKLOAD = Workload(Config())
    WORKLOAD.get_events()
    WORKLOAD.print_summary()


        
        
