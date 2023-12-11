#!/bin/bash
# this script is for a CRON job ingest
cd /home/rits/oracc-rest
source venv/bin/activate
python3 -m ingest.bulk_upload
echo "ingest complete"