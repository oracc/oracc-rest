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


def await_healthy(es: Elasticsearch, wait: int) -> None:
    """
    Wait for an Elasticsearch instance to become healthy.

    :param es: The Elasticsearch instance.
    :param wait: How many seconds to wait.

    :raises: Exception if health check does not return 'green' or 'yellow'
    within the time allowed.
    """
    end_time = time.monotonic() + wait
    while True:
        try:
            health_result = es.cat.health(h=['status']).strip()
            LOGGER.info("Health result: >%s<", health_result)
            if health_result in ['green', 'yellow']:
                return
        except elasticsearch.exceptions.ConnectionError as e:
            pass
        time.sleep(3)
        if end_time < time.monotonic():
            raise Exception("Elasticsearch unhealthy")


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

    es = Elasticsearch(args.host)
    if args.wait:
        await_healthy(es, args.wait)
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
