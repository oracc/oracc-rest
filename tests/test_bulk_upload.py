import time

import ingest.bulk_upload


def test_upload_entries(es, entries, test_index_name):
    """Test that a list of entries is indexed correctly into ElasticSearch."""
    assert ingest.bulk_upload.INDEX_NAME == test_index_name  # paranoia
    ingest.bulk_upload.upload_entries(es, entries)
    time.sleep(2)  # a small delay to make sure the upload has finished
    # Check that all documents have been uploaded
    assert es.count(index=test_index_name)["count"] == len(entries)
