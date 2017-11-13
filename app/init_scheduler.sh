#!/bin/bash
python app/scheduler.py  $1 --redisHost $2 --redisPort 6379 2>&1 | python app/queuelogger.py