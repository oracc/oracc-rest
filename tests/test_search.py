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
