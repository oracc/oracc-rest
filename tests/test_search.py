import time

import pytest

import ingest.bulk_upload
from oracc_rest import ESearch


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


def test_sort_field_name():
    """Check that we construct the sorting field argument for ES correctly."""
    search = ESearch()
    combinations = [
        ("cf", "asc", "cf.sort"),
        ("cf", "desc", "-cf.sort"),
        ("gw", "asc", "gw.keyword"),
        ("gw", "desc", "-gw.keyword"),
        ("icount", "asc", "icount"),
        ("icount", "desc", "-icount"),
    ]
    for (field, dir, expected) in combinations:
        assert search._sort_field_name(field, dir) == expected


def test_list_all(uploaded_entries, test_index_name):
    """Check that the list_all endpoint returns all the entries."""
    search = ESearch(index_name=test_index_name)
    # Note that we have to sort by something other than cf (the default),
    # because the upload process for the tests does not create the cf.sort
    # field.
    assert len(search.list_all(sort_by="gw")) == len(uploaded_entries)


def test_multi_word_search(uploaded_entries, test_index_name):
    """
    Check that the main endpoint gives the right results for basic use cases.

    Specifically, this tests that partial matching works correctly, and that
    a multi-word query gives the intersection of results, as expected.
    """
    # The test glossary that we use contains two entries for the word "goddess",
    # one for "god", and one for "snake".
    search = ESearch(index_name=test_index_name)
    # Check that we get partial matches ("god" should also match "goddess")
    assert len(search.run("god", sort_by="gw")) == 3
    # Check that the whole query word has to match (just in case!)
    assert len(search.run("goddess", sort_by="gw")) == 2
    # Check that a multi-word query returns results matching all words in it,
    # or an empty result-set if no such combination exists.
    # ("usan" is one of the words meaning "goddess"; there are no snake gods).
    assert len(search.run("god usan", sort_by="gw")) == 1
    assert not search.run("god snake", sort_by="gw")


def test_suggest_basic(uploaded_entries, test_index_name):
    """Check the basic behaviour of the suggestion endpoint.

    More specifically, ensure that we return a list that contains vaguely
    relevant results.
    """
    search = ESearch(index_name=test_index_name)
    results = search.suggest("apsu")
    # Check the returned type.
    assert isinstance(results, list)
    # Check that we match a term with two substitutions...
    assert "apši" in results
    # ...but not unrelated results.
    assert "kirir" not in results


def test_suggest_short_word(uploaded_entries, test_index_name):
    """Check that we can get suggestions for 3-letter words.

    This is important because the term suggester only returns terms of length
    4 or more by default, but our data contains shorter words.
    """
    search = ESearch(index_name=test_index_name)
    results = search.suggest("gos")
    # Check that we match a short term.
    assert "god" in results


def test_suggest_no_duplicates(uploaded_entries, test_index_name):
    """Check that the returned suggestions contain no duplicates."""
    search = ESearch(index_name=test_index_name)
    results = search.suggest("goddes")  # intentionally misspelled
    # The term "goddess" appears in multiple fields/entries in the test data
    # but should only appear in the results once.
    assert results  # to make sure the assertion below isn't trivially true!
    assert len(results) == len(set(results))

def test_completion(uploaded_entries, test_index_name):
    """Check completions work
    """
    search = ESearch(index_name=test_index_name)
    results = search.complete("g")
    # Check that we can complete from one letter and check that we have no duplicates (set in the method)
    assert results == ["god", "goddess"]

def test_completion_cf(uploaded_entries, test_index_name):
    """Check completions work
    """
    search = ESearch(index_name=test_index_name)
    results = search.complete("u")
    # Check that we can complete from one letter and check that we have no duplicates (set in the method)
    assert "usan" in results