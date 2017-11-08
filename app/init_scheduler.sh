#!/bin/bash
python scheduler.py  /usr/src/data/data.encrypted --redisHost redis --redisPort 6379 2>&1 | python queuelogger.py