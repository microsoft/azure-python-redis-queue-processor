"""
This script will pull messages from the Job Status Queue and print out the messages that show total status.
"""

from datetime import datetime
import json
import time
from app.config import Config
from app.workloadTracker import WorkloadEventType, WorkloadEvent
from azure.storage.queue import QueueService

class WorkloadEvent(object):
    def __init__(self, event_type, timestamp, contents):
        self.event_type = event_type
        self.timestamp = timestamp
        self.contents = contents

class Workload(object):

    def __init__(self, config):
        self.config = config
        self.log_queue_service = QueueService(account_name=self.config.storage_account_name,
                sas_token=self.config.workload_tracker_sas_token)
        self.workload_complete_event = None
        self.scheduler_start_event = None
        self.jobs_queued_done = None
        self.processor_events = []
        self.processor_fork_events = []
        self.job_consolidation_status_events = []
        self.job_processing_status_events = []

    def get_events(self):
        print "Getting Relevant Workload Events"
        while True:
            # Setting message visibility to 2 days, so that the message won't get processed again
            messages = self.log_queue_service.get_messages(self.config.workload_tracker_queue_name, 32)
            for msg in messages:
                parsed = json.loads(msg.content)
                event = WorkloadEvent(WorkloadEventType(parsed["event_type"]), msg.insertion_time, parsed["content"])  

                # Workload Completed
                if event.event_type == WorkloadEventType.WORKLOAD_DONE:
                    self.workload_complete_event = event

                # Scheduler - Main Start
                if event.event_type == WorkloadEventType.SCHEDULER_START:
                    self.scheduler_start_event = event
                
                # Processor - Main Start
                if event.event_type == WorkloadEventType.PROCESSOR_START:
                    self.processor_events.append(event)
                
                # Processor - Fork Start
                if event.event_type == WorkloadEventType.PROCESSOR_FORK_START:
                    self.processor_fork_events.append(event)
                
                # Job Consolidation Status
                if event.event_type == WorkloadEventType.WORKLOAD_CONSOLIDATION_STATUS:
                    self.job_consolidation_status_events.append(event)
                
                # Job Processing Status
                if event.event_type == WorkloadEventType.WORKLOAD_PROCESSING_STATUS:
                    self.job_processing_status_events.append(event)
                
                # All Jobs Queued
                if event.event_type == WorkloadEventType.JOBS_QUEUE_DONE:
                    self.jobs_queued_done = event

                if event is not None:
                    print str(event.timestamp) + " " + event.contents
            
                # Delete the message
                self.log_queue_service.delete_message(self.config.workload_tracker_queue_name, msg.id, msg.pop_receipt)

            # Stop when the workload is completed    
            if self.workload_complete_event is not None and self.scheduler_start_event is not None:
                break

            # Sleeping to avoid spamming if the queue is empty
            if not messages:
                time.sleep(10)
    
    def time_elapse(self, evt1, evt2):
        return divmod((evt2.timestamp - evt1.timestamp).total_seconds(), 60)
    
    def print_summary(self):
        print "\nSummary: "
        print "Scheduler Started: " + str(self.scheduler_start_event.timestamp)
        print "Workload Completed: " + str(self.workload_complete_event.timestamp)
        
        # Jobs Queued
        print "All Jobs Queued: " + str(self.jobs_queued_done.timestamp)
        elapse = self.time_elapse(self.scheduler_start_event, self.jobs_queued_done)
        print "Jobs Queued Elapsed Time: " + str(elapse[0]) + " mins, " + str(elapse[1]) + " secs" 
        
        # Workload Completion
        elapse = self.time_elapse(self.scheduler_start_event, self.workload_complete_event)
        print "Workload Elapsed Time: " + str(elapse[0]) + " mins, " + str(elapse[1]) + " secs" 
        
        # Processor Information
        self.processor_events.sort(key=lambda evt: evt.timestamp)
        print "Number of Processors: " + str(len(self.processor_events))
        print "\tNumber of Forked Processors Instances: " + str(len(self.processor_fork_events))
        print "\tFirst Processor Up: " + str(self.processor_events[0].timestamp)
        print "\tLast Processor Up: " + str(self.processor_events[-1].timestamp)

        # Job Processor Completion
        self.job_processing_status_events.sort(key=lambda evt: evt.timestamp)
        print "Final Processing Time: " + str(self.job_processing_status_events[-1].timestamp)
        elapse = self.time_elapse(self.scheduler_start_event, self.job_processing_status_events[-1])
        print "Processing Elapsed Time: " + str(elapse[0]) + " mins, " + str(elapse[1]) + " secs" 

if __name__ == "__main__":
    WORKLOAD = Workload(Config())
    WORKLOAD.get_events()
    WORKLOAD.print_summary()


        
        
