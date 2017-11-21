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
```
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
```

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

# Setup
TODO: Add instructions for the following:
* Create RSA Key
* Generate AES Key
* Encrypt data
* Upload to Blob

# Deployment
We will be using ARM to deploy the scheduler and processing topology to Azure.

0. Pre-req:
    * Storage acccount to upload scripts, logs, and results
    * Azure KeyVault to generate RSA Key and store ssh secrets
    * Local AES Key to encrypt data and uploaded to blob

1. Make a copy of the <i>config/config.example.json</i> and update the values appropriately

    ```cp config/config.example.json config/config.json```

2. Run the build script to package, encrypt, and upload the code to the Storage Account

    ```sh build.sh```

3. Update the <i>arm/azuredeploy.parameters.json</i> with the storage account information, custom data, and ssh keys
    * For custom data use the value inside the <i>config/config.json.encoded</i>

4. Create a resource group to deploy the topology

    ```az group create -n test1 -l westus2```

4. Deploy topology using ARM template

    ```az group deployment create --template-file arm/azuredeploy.json --parameters arm/azuredeploy.parameters.json -g test1```

# Debugging
## How to find the custom scripts execution logs
1. Get the jumpbox's public address on the Azure Portal or by executing the command:

    ```az network public-ip list -g MyResourceGroup | grep fqdn```

2. SSH into the jumpbox via password or SSH key

    ```ssh adminRQ@mydomain.westus2.cloudapp.azure.com```

3. Find the IP address of a scheduler or worker node. You can either look at the <b>VNET</b> in the Azure portal or use the CLI and get one for a specific instance. Ex: instance "3" of the worker VMSS

    ```az vmss nic list-vm-nics -g MyResourceGroup --vmss-name workerVmss --instance-id 3 | grep privateIpAddress```

4. SSH into one of those nodes

    ```ssh adminBR@10.0.2.7```

5. You need admin access to navigate to the custom scripts folder

    ```sudo -s```

6. Navigate to where ther custom script jobs are executed. Ex: execution "1"

    ```cd /var/lib/waagent/custom-script/download/1/```

7. You can look at the "stderr" and "stdout" log files to help debug what happened during deployment.

## How to view the logs of a background task
1. SSH into the desired box
2. Find the process identifier (PID)

    ```ps -aux | grep python```

3. You can view the logs for the process by doing the following 
    
    ```cat /proc/<PID>/fd/2```

## Remote in via SSH Keys
1. Copy the SSH private key to jumpbox

    ```scp -i ~/.ssh/mykey_id_rsa ~/.ssh/mykey_id_rsa admin@public-ip.westus2.cloudapp.azure.com:~/.ssh/id_rsa```

2. Remote into the Jumpbox

    ```ssh admin@public-ip.westus2.cloudapp.azure.com -i ~/.ssh/mykey_id_rsa```

3. Now you can remote to other nodes without needing to provide a password.

## Explore Redis Cache via Docker
1. Make sure your container is up and then on another shell you can exec and attach to the redis cli.

    ```docker exec -it redis redis-cli```

2. Once attached you can perform actions such as "List All Keys"

    ```127.0.0.1:6379> KEYS *```

# FAQ
## How to assign a role to a service principal?
1. Get the applicationId of the service principal.
2. Execute the following command, passing the role you want to assign to the service principal 

    ```az role assignment create --assignee <SP Application Id> --role <Reader, Contribtor,...>```