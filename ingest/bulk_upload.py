import glob
import sys

import elasticsearch
import elasticsearch.client
import elasticsearch.helpers

from .break_down import process_file


INDEX_NAME = "oracc"
TYPE_NAME = "entry"


def debug(msg):
    print(msg)


def upload_entries(es, entries):
    for entry in entries:
        entry["_index"] = INDEX_NAME
        entry["_type"] = TYPE_NAME
    elasticsearch.helpers.bulk(es, entries)


def upload_file(es, input_file):
    upload_entries(es, process_file(input_file, write_file=False))


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

    # Create an additional field used for sorting. The new field is called
    # cf.sort and will use a locale-aware collation. We need to do this before
    # ingesting the data, so that the new field is properly populated.
    # TODO Check that the ICU plugin exists? (or mapping creation will likely fail)
    client.create(index=INDEX_NAME)
    body = {
        "properties": {
            "cf": {
                "type": "text",
                "fields": {
                    "sort": {
                        "type": "icu_collation_keyword"
                    }}}}}
    client.put_mapping(index=INDEX_NAME, doc_type=TYPE_NAME, body=body)

    # for each file:
    for file in files:
        # break down into individual entries and upload to ES using the bulk API
        upload_file(es, file)
