import glob
import sys

import elasticsearch
import elasticsearch.client
import elasticsearch.helpers

from break_down import process_file


INDEX_NAME = "oracc"
TYPE_NAME = "entry"  # ES6 only allows one type per index, so maybe not needed


def debug(msg):
    print(msg)


def upload_file(es, input_file):
    entries = process_file(input_file, write_file=False)
    for entry in entries:
        entry["_index"] = INDEX_NAME
        entry["_type"] = TYPE_NAME
    elasticsearch.helpers.bulk(es, entries)


if __name__ == "__main__":
    clear_database = True

    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = glob.glob("neo/gloss-???.json")
    debug("Will index {}".format(",".join(files)))

    # clear ES database if desired
    es = elasticsearch.Elasticsearch()
    client = elasticsearch.client.IndicesClient(es)
    if clear_database:
        try:
            debug("Will delete index " + INDEX_NAME)
            client.delete(INDEX_NAME)
        except elasticsearch.exceptions.NotFoundError:
            debug("Index not found, continuing")

    # for each file:
    for file in files:
        # break down into individual entries and upload to ES using the bulk API
        upload_file(es, file)
