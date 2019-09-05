"""Methods for creating an index for Oracc glossary data."""
from elasticsearch_dsl import analyzer, char_filter, Index


def prepare_index_mapping():
    """Create the mapping to be used for the index.

    These must be specified before ingesting the data, so that the fields are
    properly populated.
    """
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
    mappings = {"properties": field_properties}
    return mappings


def prepare_cuneiform_analyzer():
    """Create an analyzer to handle cuneiform transliterations.

    Some fields will contain non-ASCII characters. We want these characters
    to be searchable by some equivalent ASCII sequences, according to the
    Oracc conventions. For this, we need a custom analyzer that will replace
    the non-ASCII characters with their "equivalents".

    For the list of character substitutions that we allow, see:
    http://oracc.museum.upenn.edu/doc/search/searchingcorpora/index.html#h_asciinonunicode

    For more information on Elasticsearch analyzers and their components, see:
    https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html
    """
    # First we define the character filter that will do the replacement.
    cuneiform_to_ascii = char_filter(
        "cuneiform_to_ascii",
        type="mapping",
        mappings=[
            "š => sz",
            "ṣ => s."
        ]
    )
    # Now we define the analyzer using this character filter and some builtins.
    cuneiform_analyzer = analyzer(
        "cuneiform_analyzer",
        # The standard tokenizer will remove "," and ".", which are
        # used in some substitution sequences; instead, we can break
        # tokens on whitespace, which will ignore punctuation.
        tokenizer="whitespace",
        filter=["lowercase"],
        char_filter=cuneiform_to_ascii
    )
    return cuneiform_analyzer


def create_index(es, index_name, type_name):
    """
    Create an index to handle glossary data.

    This will apply the necessary settings and mappings so that data can be
    processed and searched correctly.

    :param es: an Elasticsearch instance to connect to
    :param index_name: the name of the index to create
    :param type_name: the name of the document type to apply the mappings to
    """
    index = Index(index_name)
    index.analyzer(prepare_cuneiform_analyzer())
    index.create(using=es)
    mappings = prepare_index_mapping()
    index.put_mapping(using=es, doc_type=type_name, body=mappings)
