import time

from elasticsearch_dsl import Index, Search

import ingest.bulk_upload
from ingest.prepare_index import (ANALYZER_NAME, create_index,
                                  prepare_cuneiform_analyzer)


def test_analyzer(es, test_index_name):
    """Test that the analyzer follows the Oracc non-ASCII representation."""
    analyzer = prepare_cuneiform_analyzer()
    index = Index(test_index_name)
    index.analyzer(analyzer)
    index.create(using=es)
    # Check various character substitutions work
    original_texts = ["ḫa", "ŋen", "ṣa", "ša", "ṭa"]
    analyzed_texts = ["ha", "jen", "s,a", "sza", "t,a"]
    for (original, analyzed) in zip(original_texts, analyzed_texts):
        response = index.analyze(
            using=es, body={"text": original, "analyzer": ANALYZER_NAME})
        assert response["tokens"][0]["token"] == analyzed
    # Check a text consisting of multiple words
    combined_original = " ".join(original_texts)
    response = index.analyze(
        using=es, body={"text": combined_original, "analyzer": ANALYZER_NAME})
    tokens = [block["token"] for block in response["tokens"]]
    assert tokens == analyzed_texts


def test_upload_entries(es, entries, test_index_name):
    """Test that a list of entries is indexed correctly into ElasticSearch."""
    assert ingest.bulk_upload.INDEX_NAME == test_index_name  # paranoia
    ingest.bulk_upload.upload_entries(es, entries)
    time.sleep(2)  # a small delay to make sure the upload has finished
    # Check that all documents have been uploaded
    assert es.count(index=test_index_name)["count"] == len(entries)


def test_analyzer_search_results(es, entries, test_index_name):
    """Test that the analyzer works as expected at search time."""
    # Create the index with all the required settings
    create_index(es, test_index_name, ingest.bulk_upload.TYPE_NAME)
    ingest.bulk_upload.upload_entries(es, entries)
    time.sleep(2)  # a small delay to make sure the upload has finished
    # The test entries include "apši". Check that its ASCII transliteration
    # can be retrieved.
    search = Search(using=es, index=test_index_name).query("match", cf="apszi")
    results = search.execute()
    assert len(results) == 1  # would be 0 if no results found
    assert results[0].cf == "apši"
