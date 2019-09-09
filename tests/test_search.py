from oracc_rest import ESearch


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
