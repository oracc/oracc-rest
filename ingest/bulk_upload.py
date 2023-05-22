import glob
import sys

import elasticsearch
import elasticsearch.client
import elasticsearch.helpers

from .break_down import process_file
from .prepare_index import create_index

INDEX_NAME = "oracc"


def debug(msg):
    print(msg)


def upload_entries(es, entries):
    for entry in entries:
        entry["_index"] = INDEX_NAME
        entry["completions"] = [entry["cf"], entry["gw"]]
    elasticsearch.helpers.bulk(es, entries)


def upload_file(es, input_file):
    upload_entries(es, process_file(input_file, write_file=False))


def ICU_installed(es):
    """Check whether the ICU Analysis plugin is installed locally."""
    cc = elasticsearch.client.CatClient(es)
    return "analysis-icu" in [p["component"] for p in cc.plugins(format="json")]


if __name__ == "__main__":
    es = elasticsearch.Elasticsearch()
    if not ICU_installed(es):
        debug("ICU Analysis plugin is required but could not be found. Exiting.")
        sys.exit()

    clear_database = True

    if len(sys.argv) > 1:
        files = sys.argv[1:]
        print(files)
    else:
        files = glob.glob("neo/gloss-???.json")
    debug("Will index {}".format(",".join(files)))

    # Clear ES database if desired
    client = elasticsearch.client.IndicesClient(es)
    if clear_database:
        try:
            debug("Will delete index " + INDEX_NAME)
            client.delete(INDEX_NAME)
        except elasticsearch.exceptions.NotFoundError:
            debug("Index not found, continuing")

    # Create the index with the required settings
    create_index(es, INDEX_NAME)

    for file in files:
        # Break down into individual entries and upload to ES using the bulk API
        upload_file(es, file)
