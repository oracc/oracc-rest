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


def ICU_installed(es):
    """Check whether the ICU Analysis plugin is installed locally."""
    cc = elasticsearch.client.CatClient(es)
    return 'analysis-icu' in [p['component'] for p in cc.plugins(format="json")]


def prepare_index_settings():
    """Create the mapping and settings to be used for the index.

    These must be specified before ingesting the data, so that the fields are
    properly populated.
    """
    # Some fields will contain non-ASCII characters. We want these characters
    # to be searchable by some equivalent ASCII sequences, according to the
    # Oracc conventions. For this, we need a custom analyzer that will replace
    # the non-ASCII characters with their "equivalents".
    analysis_properties = {
        "analyzer": {
            "cuneiform_analyzer": {
                # The standard tokenizer will remove "," and ".", which are
                # used in some substitution sequences; instead, we can break
                # tokens on whitespace, which will ignore punctuation.
                "tokenizer": "whitespace",
                "filter": ["lowercase"],
                "char_filter": ["cuneiform_to_ascii"]
            }
        },
        # For the list of character substitutions, see
        # http://oracc.museum.upenn.edu/doc/search/searchingcorpora/index.html#h_asciinonunicode
        "char_filter": {
            "cuneiform_to_ascii": {
                "type": "mapping",
                "mappings": [
                    "š => sz",
                    "ṣ => s."
                ]
            }
        }
    }
    # Create an additional field used for sorting. The new field is called
    # cf.sort and will use a locale-aware collation.
    field_properties = {
        "cf": {
            "type": "text",
            "analyzer": "cuneiform_analyzer",
            "fields": {
                "sort": {
                    "type": "icu_collation_keyword"
                }
            }
        }
    }

    settings = {"analysis": analysis_properties}
    mappings = {"properties": field_properties}
    return settings, mappings


if __name__ == "__main__":
    es = elasticsearch.Elasticsearch()
    if not ICU_installed(es):
        debug("ICU Analysis plugin is required but could not be found. Exiting.")
        sys.exit()

    clear_database = True

    if len(sys.argv) > 1:
        files = sys.argv[1:]
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
    settings, mappings = prepare_index_settings()
    client.create(index=INDEX_NAME, body={"settings": settings})
    client.put_mapping(index=INDEX_NAME, doc_type=TYPE_NAME,
                       body=mappings)

    for file in files:
        # Break down into individual entries and upload to ES using the bulk API
        upload_file(es, file)
