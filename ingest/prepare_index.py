"""Methods for creating an index for Oracc glossary data."""
from elasticsearch_dsl import analyzer, char_filter, Field, Index, Mapping


ANALYZER_NAME = "cuneiform_analyzer"
CHAR_FILTER_NAME = "cuneiform_to_ascii"


class ICUKeywordField(Field):
    """A class to represent fields of type icu_collation_keyword.

    We need to define this as the DSL does not recognise field names from
    plugins.
    """
    name = "icu_collation_keyword"


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
    synonyms = {"ḫ": "h", "ŋ": "j", "ṣ": "s,", "š": "sz", "ṭ": "t,",
                # Unicode "positions" of vowel variants do not follow any
                # pattern, so they must be listed explicitly:
                "á": "a2", "à": "a3", "â": "a", "ā": "a",
                "é": "e2", "è": "e3", "ê": "e", "ē": "e",
                "í": "i2", "ì": "i3", "î": "i", "ī": "i",
                "ú": "u2", "ù": "u3", "û": "u", "ū": "u",
                }
    # Numerical subscript characters (₀, ₁, etc) run contiguously from 0x2080.
    # We map them to their "normal" digits, so that e.g. ₁ is matched by 1.
    for digit in range(10):
        synonyms[chr(8320 + digit)] = str(digit)
    cuneiform_to_ascii = char_filter(
        CHAR_FILTER_NAME,
        type="mapping",
        mappings=["{} => {}".format(*pair) for pair in synonyms.items()],
    )
    # Now we define the analyzer using this character filter and some builtins.
    cuneiform_analyzer = analyzer(
        ANALYZER_NAME,
        # The standard tokenizer will remove "," and ".", which are
        # used in some substitution sequences; instead, we can break
        # tokens on whitespace, which will ignore punctuation.
        tokenizer="whitespace",
        filter=["lowercase"],
        char_filter=cuneiform_to_ascii
    )
    return cuneiform_analyzer


def prepare_index_mapping(doc_type):
    """Create the field mappings in the index for the specified type.

    These must be specified before ingesting the data, so that the fields are
    properly populated.
    """
    mappings = Mapping(doc_type)
    # Create an additional field used for sorting. The new field is called
    # cf.sort and will use a locale-aware collation.
    # The base cf field will use the custom cuneiform analyzer.
    mappings.field("cf", "text", analyzer=ANALYZER_NAME,
                   fields={"sort": ICUKeywordField()})
    # Also use the analyzer for other fields which contain cuneiform text.
    for field in ["forms_n", "norms_n"]:
        # TODO Do we lose anything by making this mapping explicit? (compared
        # to the dynamic mapping created by Elasticsearch automatically)
        mappings.field(field, "text", analyzer=ANALYZER_NAME)
    # Add completions field to index
    mappings.field("completions", "completion")    
    return mappings


def create_index(es, index_name, type_name):
    """
    Create an index to handle glossary data.

    This will apply the necessary settings and mappings so that data can be
    processed and searched correctly.

    :param es: an Elasticsearch instance to connect to
    :param index_name: the name of the index to create
    :param type_name: the name of the document type to apply the mappings to
    """
    index = Index(index_name, doc_type=type_name)
    index.analyzer(prepare_cuneiform_analyzer())
    index.mapping(prepare_index_mapping(type_name))
    index.create(using=es)
