#!/bin/bash
# this script is for a CRON job ingest
# no input folder is given as it assumes oracc-rest/neo
# if this is not correct just add a path after ingest.bulk_upload
# eg. ingest.bulk_upload ingest/assets/dev/sample-glossaries/*
cd /home/rits/oracc-rest
source venv/bin/activate
python3 -m ingest.bulk_upload
echo "ingest complete"
