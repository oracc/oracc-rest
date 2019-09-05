"""Methods for creating an index for Oracc glossary data."""
import elasticsearch


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


def create_index(es, index_name, type_name):
    """
    Create an index to handle glossary data.

    This will apply the necessary settings and mappings so that data can be
    processed and searched correctly.

    :param es: an Elasticsearch instance to connect to
    :param index_name: the name of the index to create
    :param type_name: the name of the document type to apply the mappings to
    """
    client = elasticsearch.client.IndicesClient(es)
    settings, mappings = prepare_index_settings()
    client.create(index=index_name, body={"settings": settings})
    client.put_mapping(index=index_name, doc_type=type_name,
                       body=mappings)
