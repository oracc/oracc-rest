#!/bin/bash
# this script is for a CRON job ingest
# no input folder is given to the python call as it assumes oracc-rest/neo
# if this is not correct just add a path after ingest.bulk_upload
# eg. ingest.bulk_upload ingest/assets/dev/sample-glossaries/*

cd /home/rits/oracc-rest
source venv/bin/activate

# Run the ingest script and capture the outcome in journal
systemd-cat -t cron-ingest python3 -m ingest.bulk_upload

echo "Ingest complete. Run journalctl -t cron-ingest for logs."