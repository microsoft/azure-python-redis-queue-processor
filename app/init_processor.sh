#!/bin/bash
python processor.py ../data/aes.encrypted --redisHost redis --redisPort 6379 2>&1 | python queuelogger.py