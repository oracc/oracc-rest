import time

from elasticsearch_dsl import Index

import ingest.bulk_upload
from ingest.prepare_index import ANALYZER_NAME, prepare_cuneiform_analyzer


def test_analyzer(es, test_index_name):
    """Test that the analyzer follows the Oracc non-ASCII representation."""
    analyzer = prepare_cuneiform_analyzer()
    index = Index(test_index_name)
    index.analyzer(analyzer)
    index.create(using=es)
    # Check various character substitutions work
    for (text, analyzed) in [("apši", "apszi"), ("ṣa", "s,a")]:
        response = index.analyze(
            using=es, body={"text": text, "analyzer": ANALYZER_NAME})
        assert response["tokens"][0]["token"] == analyzed


def test_upload_entries(es, entries, test_index_name):
    """Test that a list of entries is indexed correctly into ElasticSearch."""
    assert ingest.bulk_upload.INDEX_NAME == test_index_name  # paranoia
    ingest.bulk_upload.upload_entries(es, entries)
    time.sleep(2)  # a small delay to make sure the upload has finished
    # Check that all documents have been uploaded
    assert es.count(index=test_index_name)["count"] == len(entries)
