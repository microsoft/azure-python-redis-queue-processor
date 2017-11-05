# Using Docker for local dev

## Requirements
* [Docker](https://docs.docker.com/engine/installation/)
* Docker Compose (usually installed with docker)

## Building
* `docker-compose build`


## Execution
### Redis
* `docker-compose up redis`
* You can pass `-d` flag for running in background

### Redis queue web UI
* `docker-compose up dashboard`
* You can pass `-d` flag for running in background
* Open browser and navigate to [localhost:8080](http://localhost:8080)

### Scheduler
* `docker-compose up scheduler`
* This executes the app/scheduler.py in docker environment
* The scheduler will read a data file and queue a job for each row of data

### Processor
* `docker-compose up processor`
* This executes the app/processor.py in docker environment
* The processor unwraps an AES key used for decrypting each job's data record, then it runs a RQ worker

## Other Containers for testing

### Run worker (shell mode)
* Redis queue allows you to run the workers just by running the `rq worker` command.
* To do this in isolated docker environment run `docker-compose up worker`

### Run worker (python scrypt mode)
* Redis queue allows you to run the workers just by running a python script (see `app/worker.py`)
* To do this in isolated docker environment run `docker-compose up worker-script`

### Run job manager
* `docker-compose up manager`
* This command executes `app/manager.py` in docker environment.