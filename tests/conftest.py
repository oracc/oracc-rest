import json
import warnings

from elasticsearch import Elasticsearch, exceptions
from elasticsearch.client import IndicesClient
import pytest

import ingest.bulk_upload


@pytest.fixture(scope="session")
def index_name():
    """The name of the fake index to use throughout the tests."""
    return "oracc_test"


@pytest.fixture
def es(monkeypatch, index_name):
    """An ElasticSearch client which also ensures we operate on a fake index."""
    # NB: INDEX_NAME cannot be imported directly, or the patching won't work.
    # Also note that this fixture cannot be module-scoped because monkeypatch is
    # function-scoped.
    monkeypatch.setattr(ingest.bulk_upload, "INDEX_NAME", index_name)
    assert ingest.bulk_upload.INDEX_NAME == index_name  # just making sure
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
