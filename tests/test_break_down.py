import json

from break_down import process_file, base_fields, direct_fields, indirect_fields


def test_process_file():
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
        # Check that the direct fields are copied correctly
        for field in direct_fields:
            new_entry[field] = old_entry[field]
        # And the same for the indirect fields
        # For an example of how the output should be like, look at gloss-elx-out.json
        for field in indirect_fields:
            for nested_field in indirect_fields[field]:
                nested_name = "{}_{}".format(field, nested_field)
                for value in old_entry[field]:
                    assert value[nested_field] in new_entry[nested_name]
