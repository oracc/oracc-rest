#!/bin/bash
# this script is for a CRON job ingest
# no input folder is given to the python call as it assumes oracc-rest/neo
# if this is not correct just add a path after ingest.bulk_upload
# eg. ingest.bulk_upload ingest/assets/dev/sample-glossaries/*
# logs will accumulate in the LOG_FILE given

LOG_FILE="/home/rits/oracc-rest/ingest.log"

cd /home/rits/oracc-rest
source venv/bin/activate

# Run the ingest script and capture the outcome
python3 -m ingest.bulk_upload 2>&1 | tee -a "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - Ingest process completed" >> "$LOG_FILE"

echo "Ingest complete. See $LOG_FILE for details."