import logging
import uuid
import time
import socket
from results import Results

logger = logging.getLogger(__name__)

def initLogging():
    logger.setLevel(logging.DEBUG)
    # setup a console logger by default
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s test.py ' + socket.gethostname() +' %(levelname)-5s %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

if __name__ == "__main__":
    initLogging()

    results = Results(logger, 'localhost', 6379)

    resultsCount = results.count_consolidated_results()

    print("Results count: " + str(resultsCount))

    for x in range(100):
        results.write_result(str(uuid.uuid4()), "result content " + str(x))
        print("Created results blob #" + str(x))

    resultsCount = results.count_consolidated_results()

    print("Results count: " + str(resultsCount))

    # sleep for 5 seconds to allow blob consistency to catch up
    time.sleep(5)

    consolidatedResults = results.consolidate_results()

    print("Consolidated results: " + str(consolidatedResults))