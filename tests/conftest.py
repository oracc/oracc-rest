import json
import time
import warnings

from elasticsearch import Elasticsearch, exceptions
from elasticsearch.client import IndicesClient
import pytest

import ingest.bulk_upload


@pytest.fixture(scope="session")
def test_index_name():
    """The name of the fake index to use throughout the tests."""
    return "oracc_test"


@pytest.fixture
def es(monkeypatch, test_index_name):
    """An ElasticSearch client which also ensures we operate on a fake index."""
    # NB: INDEX_NAME cannot be imported directly, or the patching won't work.
    # Also note that this fixture cannot be module-scoped because monkeypatch is
    # function-scoped.
    monkeypatch.setattr(ingest.bulk_upload, "INDEX_NAME", test_index_name)
    assert ingest.bulk_upload.INDEX_NAME == test_index_name  # just making sure
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


@pytest.fixture
def uploaded_entries(es, entries, test_index_name):
    """A fixture to ensure that the test glossary entries have been uploaded."""
    ingest.bulk_upload.upload_entries(es, entries)
    # Wait until the upload has finished, but give up after about 10 seconds.
    number_attempts = 20  # how many times to check before giving up
    delay = 0.5  # how long to sleep between attempts
    for _ in range(number_attempts):
        if es.count(index=test_index_name)["count"] == len(entries):
            return entries  # all uploaded!
        else:
            time.sleep(delay)
    assert False  # raise an error if upload not complete after all attempts
