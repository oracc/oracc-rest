import argparse
import glob
import logging
import sys
import time
import urllib3

import elasticsearch
from elasticsearch import Elasticsearch
import elasticsearch.client
import elasticsearch.helpers

from .break_down import process_file
from .prepare_index import create_index

INDEX_NAME = "oracc"

LOGGER = logging.getLogger("bulk_upload")

def upload_entries(es, entries):
    for entry in entries:
        entry["_index"] = INDEX_NAME
        entry["completions"] = [entry["cf"], entry["gw"]]
    elasticsearch.helpers.bulk(es, entries, index=INDEX_NAME)


def upload_file(es, input_file):
    upload_entries(es, process_file(input_file, write_file=False))


def ICU_installed(es):
    """Check whether the ICU Analysis plugin is installed locally."""
    cc = elasticsearch.client.CatClient(es)
    return "analysis-icu" in [p["component"] for p in cc.plugins(h=None, format="json")]

def wait_for_elasticsearch(host: str, wait: int) -> None:
    """
    Wait for elasticsearch to be available and healthy.

    :param host: Host at which elasticsearch resides, for example
    "http://localhost:9200".
    :param wait: Number of seconds to wait before giving up and
    throwing an exception.
    :return: A non-exceptional return indicates that elasticsearch is healthy.
    """
    url = f"{host}/_cluster/health?wait_for_status=yellow&timeout=3s"
    http = urllib3.PoolManager(num_pools=2)
    now = time.monotonic()
    end = now + wait
    attempt = 0
    while now < end:
        attempt += 1
        try:
            resp = http.request("GET", url, timeout=4)
            if resp.status == 200:
                LOGGER.debug("elasticsearch is ready")
                return
            LOGGER.debug("elasticsearch is not ready %d", attempt)
        except urllib3.exceptions.MaxRetryError:
            LOGGER.debug("elasticsearch is not available")
        time.sleep(3)
        next = time.monotonic()
        time.sleep(max(0.5, min((end - next) * 0.7, 5)))
        now = time.monotonic()

    raise Exception("Elasticsearch is down")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Upload glossaries to ElasticSearch"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="http://localhost:9200",
        help="Specify elasticsearch host (default http://localhost:9200)",
    )
    parser.add_argument(
        "--glob",
        "-g",
        help="Expand wildcards in filenames",
        action="store_true",
    )
    parser.add_argument(
        "--wait",
        type=int,
        metavar="SECONDS",
        help="Wait for up to this many seconds for elasticsearch to be ready before uploading",
    )
    parser.add_argument(
        "filenames",
        type=str,
        nargs="*",
        help="Glossaries to upload",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if args.wait:
        wait_for_elasticsearch(args.host, args.wait)
    es = Elasticsearch(args.host, timeout=30)
    if not ICU_installed(es):
        LOGGER.debug("ICU Analysis plugin is required but could not be found. Exiting.")
        sys.exit()

    clear_database = True

    files = args.filenames
    if len(files) == 0:
        files = glob.glob("neo/gloss-???.json")
    elif args.glob:
        files = []
        for fn in args.filenames:
            files += glob.glob(fn)

    LOGGER.debug("Will index %s", ",".join(files))

    # Clear ES database if desired
    client = elasticsearch.client.IndicesClient(es)
    if clear_database:
        try:
            LOGGER.debug("Will delete index %s", INDEX_NAME)
            client.delete(index=INDEX_NAME)
        except elasticsearch.exceptions.NotFoundError:
            LOGGER.debug("Index not found, continuing")

    # Create the index with the required settings
    create_index(es, INDEX_NAME)

    for file in files:
        print(f"going to upload {file}")
        # Break down into individual entries and upload to ES using the bulk API
        upload_file(es, file)
