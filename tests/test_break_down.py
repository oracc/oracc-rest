import json

import pytest

from ingest.break_down import (
    name_and_type,
    preprocess_glossary,
    process_file,
    process_glossary_data,
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


@pytest.fixture(scope="module")
def missing_instances_glossary():
    """
    Return a glossary where some entries refer to a non-existent instance,
    along with the number of missing entries.
    """
    with open("tests/gloss-missing-instance.json", 'r') as infile:
        original_data = json.load(infile)
    return original_data, 1


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


def test_missing_instances(missing_instances_glossary):
    """Test that we skip entries with missing instances and raise a warning."""
    original_data, missing_number = missing_instances_glossary
    with pytest.warns(UserWarning):
        processed_data = process_glossary_data(original_data)
    assert len(processed_data) == len(original_data["entries"]) - missing_number


def test_preprocess():
    """Test that the preprocessing step gives the expected results."""
    # TODO Can parametrise this to test other sample files
    # TODO Should we check the properties of the output data (e.g. keys, length)
    # rather than compare it to a fixed output?
    input_file = 'tests/gloss-elx.json'
    expected_output_file = 'tests/gloss-elx-preprocessed.json'
    with open(expected_output_file, 'r') as f:
        expected_data = json.load(f)
    output_data = preprocess_glossary(input_file)
    assert output_data == expected_data


def test_name_and_type():
    """Test that the breaking down of field specs into name and type works."""
    # Check that we return the right name and str when there is no type given
    assert name_and_type("field_name") == ("field_name", str)
    # Check that we return the spec itself when it contains a type, e.g. float
    assert name_and_type(("field_name", float)) == ("field_name", float)
    # And check that this still works when the specified type is already str
    assert name_and_type(("field_name", str)) == ("field_name", str)
