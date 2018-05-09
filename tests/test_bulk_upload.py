import time
import json
import warnings

from elasticsearch import Elasticsearch, exceptions
from elasticsearch.client import IndicesClient
import pytest

import ingest.bulk_upload


INDEX_NAME = "oracc_test"


@pytest.fixture
def es(monkeypatch):
    """An ElasticSearch client which also ensures we operate on a fake index."""
    # NB: INDEX_NAME cannot be imported directly, or the patching won't work.
    # Also note that this fixture cannot be module-scoped because monkeypatch is
    # function-scoped.
    monkeypatch.setattr(ingest.bulk_upload, "INDEX_NAME", INDEX_NAME)
    assert ingest.bulk_upload.INDEX_NAME == INDEX_NAME  # just making sure
    client = Elasticsearch()
    yield client
    try:
        IndicesClient(client).delete(ingest.bulk_upload.INDEX_NAME)
    except exceptions.NotFoundError:
        warnings.warn("The ES index was never created (was anything indexed?)")


@pytest.fixture(scope="module")
def entries():
    """An example list of JSON glossary entries."""
    with open("tests/gloss-elx-out.json", "r") as entries_file:
        return json.load(entries_file)


def test_upload_entries(es, entries):
    """Test that a list of entries is indexed correctly into ElasticSearch."""
    assert ingest.bulk_upload.INDEX_NAME == INDEX_NAME  # paranoia
    ingest.bulk_upload.upload_entries(es, entries)
    time.sleep(2)  # a small delay to make sure the upload has finished
    # Check that all documents have been uploaded
    assert es.count(index=INDEX_NAME)["count"] == len(entries)
