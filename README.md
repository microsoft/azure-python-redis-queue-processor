# Introduction
High scale parallel processing architecture in Azure based on Redis RQ and written in Azure.

### Solution Characteristics
- Runs in Microsoft Azure
- Written in Python
- Queues provided by Redis and the [Python Redis RQ library](http://python-rq.org/)
- Simple Linux VMs used for scheduling and processing
- No reliance on Azure VM extensions
- Minimal cloud provider lock-in
- Encryption of all data and scripts

# Dev Setup

### Pyenv for multiple python versions (macOS)
brew install pyenv
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
exec "$SHELL"
xcode-select --install
CFLAGS="-I$(brew --prefix openssl)/include" \
LDFLAGS="-L$(brew --prefix openssl)/lib" \
pyenv install -v 2.7.5
pyenv rehash
cd <yourlocalpath>/azure-python-redis-queue-processor
pyenv local 2.7.5
python --version

### Dependencies
- [Python 2.7.5](http://https://www.python.org/download/releases/2.7.5/)
- [PIP Package Manager](https://pip.pypa.io/en/stable/installing/)
- [Git](http://https://git-scm.com/downloads)
- [Docker (for local Redis instance)](https://docker.com)

### PyPI Package Dependencies
All PyPI package dependencies are included in requirements.txt.

### Setup Instructions
1. Git clone repo
2. Install dependencies
3. Open bash shell
4. Pip install package dependencies
5. Clone `config/config.example.json` and rename it to `config.json`
6. Supply `config.json` with values for your Azure Subscription and app parameter
7. Run `sudo pip install -r requirements.txt`
8. Run `bash build.sh`


# Processing Workflow
At a high level, this repo provides a reference solution for a queue based parallel job processing solution. Jobs to be processed are queued and N number of workers pull jobs off the queue in parallel and process them.

### Job Scheduling Workflow
1. Encrypted scripts and data to be processed uploaded to Azure Blob Storage
2. Scheduler VM role deployed and executes scheduler_bootstrap.sh
3. Scheduler python script decrypted by schedulerconfiguration.py
4. Data to be processed decrypted by schedulerconfiguration.py
5. Data is parsed into jobs by scheduler.py
6. Jobs to be executed are queued to Redis RQ by scheduler.py
7. Job status records are created by scheduler.py

### Job Processing Workflow
1. Processor VM role deployed and executes processor_bootstrap.sh
2. AES key for job result encyrption downloaded by processorconfiguration.py
3. Processing job executed by processor.py
4. Job status record updated with processing state
5. Job result encrypted and written to Azure Blob Storage
6. Completed or failed job status record written out to Azure Queue for additional processing

# Metrics Logging
Microsoft Azure VM extensions are not required to be installed in this solution. Many high security institutions do not want to run third party extensions unless absolutely necessary. Basic VM metrics, such as CPU and disk, can be captured using the Azure Metrics REST APIs and remove the need for an extension to be installed on VMs.

### metricslogger.py
metricslogger.py captures basic metrics for all VMs in an Azure Resource Group using the Azure Metrics REST API. This python script can be executed as a scheduled job via a chron job or similar mechanism.

**Pre-req: Service Principal credentials with read access to all VMs**

1. Retrieves a list of all VMs in an Azure Resource Group
2. Retrieves basic metrics (CPU, disk, network) for each VM in the Resource Group
3. Stores metrics in Azure Storage for analysis
