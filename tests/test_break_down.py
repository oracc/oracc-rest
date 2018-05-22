import json

import pytest

from ingest.break_down import (
    name_and_type,
    process_file,
    base_fields,
)


@pytest.fixture(scope="module")
def direct_fields():
    """Return the names of the fields directly copied into the new entries."""
    from ingest.break_down import direct_fields as fields
    return [name_and_type(field)[0] for field in fields]


@pytest.fixture(scope="module")
def indirect_fields():
    """Return the indirect fields as a dictionary, but with any types removed."""
    from ingest.break_down import indirect_fields as fields
    return {
        outer: [name_and_type(inner)[0] for inner in fields[outer]]
        for outer in fields
    }


def test_process_file(direct_fields, indirect_fields):
    """Test that we can break down a small glossary correctly."""
    input_name = "tests/gloss-elx.json"  # modified from the original
    with open(input_name, 'r') as infile:
        original_data = json.load(infile)
    new_entries = process_file(input_name, write_file=False)
    # Make sure we have all entries
    assert len(new_entries) == len(original_data["entries"])
    # Check that the shared fields have been copied into each entry
    for entry in new_entries:
        for field in base_fields:
            assert entry[field] == original_data[field]
    for old_entry, new_entry in zip(original_data["entries"], new_entries):
        # Check that the direct fields are copied correctly (if seen as strings)
        for field in direct_fields:
            assert str(new_entry[field]) == old_entry[field]
        # Also check that the count of instances has the right type
        assert isinstance(new_entry["icount"], int)
        # And the same for the indirect fields
        # For an example of how the output should be like, look at gloss-elx-out.json
        for field in indirect_fields:
            for nested_field in indirect_fields[field]:
                nested_name = "{}_{}".format(field, nested_field)
                for value in old_entry[field]:
                    # TODO this needs some changes if the nested field is not a
                    # string (but so far this isn't the case)
                    assert value[nested_field] in new_entry[nested_name]
        # Check that the top-level instances are correctly linked
        correct_instances = original_data["instances"][old_entry["xis"]]
        assert sorted(new_entry["instances"]) == sorted(correct_instances)
