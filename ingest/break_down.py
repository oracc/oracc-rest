"""A module for breaking down a glossary into individual entries."""
import json
import os
import subprocess
import sys


# By default, we treat most glossary data as strings, but sometimes we want the
# REST API to return a different type (for instance, counts should be integers).
# The below sequences refer to fields in two ways: a field name just by itself
# indicates that the field should be indexed as a string; alternatively, if the
# name is accompanied by a type [e.g. ("icount", int)], that means that its
# values should be converted to the given type.
base_fields = ["project", "lang"]  # fields to copy into each entry
direct_fields = ["gw", "headword", "cf", ("icount", int), "id"]
indirect_fields = {
    "senses": ["mng"],
    "forms": ["n"],
    "norms": ["n"],
    "periods": ["p"]
}


def name_and_type(field_spec):
    """Break down a field spec into field name and type (string, by default)."""
    # NB We cannot just try unwrapping the spec (and assume failure means there
    # is no type), since strings can also be unwrapped, so the spec "gw" would
    # be extracted as a name ("g") and a type ("w"). Hence, we check for strings
    # explicitly.
    if isinstance(field_spec, str):  # if the spec contains only the field name
        return field_spec, str
    else:  # if the spec also has a type
        return field_spec[0], field_spec[1]


def process_entry(entry):
    """Flatten the nested fields of an entry."""
    new_entry = {}
    for field in direct_fields:
        field_name, to_type = name_and_type(field)
        new_entry[field_name] = to_type(entry[field_name])
    for top_field in indirect_fields:
        for inner_field in indirect_fields[top_field]:
            inner_field_name, to_type = name_and_type(inner_field)
            new_field = "{}_{}".format(top_field, inner_field_name)
            new_entry[new_field] = [
                        to_type(inner_entry[inner_field_name])
                        for inner_entry
                        in entry.get(top_field, [])  # in case field is missing
            ]
    # TODO Consider making this a generator (if too slow for bigger files)?
    return new_entry


def process_glossary_data(data):
    """
    Process a glossary and link the entries to their instances.

    Glossaries contain entries in a nested format. This step extracts the
    relevant information at various nesting levels, and produces a list of
    entries with "flattened" fields. It also incorporates the information from
    the instances part of the glossary into the relevant entries.
    Any entries referring to non-existent instances will be ignored. A warning
    will be raised in those cases.

    :param data: a dictionary representing a glossary, including the instances.
    :return: a list of entries, flattened and linked to instances when possible.

    """
    instances = data["instances"]
    base_data = {key: data[key] for key in base_fields}
    new_entries = []
    for entry in data["entries"]:
        # Create a flat entry from the nested norms, forms, senses etc.
        new_entry = process_entry(entry)
        # Find the instance that is referred to by the entry. For now, just link
        # the top-level reference rather than that of individual senses, norms
        # etc. Every entry should have a corresponding instance in the glossary,
        # so if something is missing this will throw a KeyError, which will let
        # us know that there is something wrong with the glossary.
        try:
            new_entry["instances"] = instances[entry["xis"]]
        except KeyError:
            print("Could not find the instance {} for entry {}!".format(
                    entry["xis"], entry["headword"]
            ))
            continue
        # Add the attributes shared by all entries in the glossary
        new_entry.update(base_data)
        new_entries.append(new_entry)
    return new_entries


def preprocess_glossary(glossary_filename):
    """Remove unused fields from a glossary and return it as a dictionary."""
    filter_file = os.path.join("ingest", "remove_unused.jq")
    s = subprocess.run(
            ["jq", "-f", filter_file, glossary_filename],
            stdout=subprocess.PIPE
    )
    # We need to decode the output to a string if not working in binary mode
    return json.loads(s.stdout.decode("utf8"))


def process_file(input_name, write_file=True):
    """
    Process all entries in a glossary file, extracting the common information to
    create entries that can be individually indexed. Optionally create a new
    file with the entries that can be uploaded manually.

    :param input_name: the name of the glossary JSON file
    :param write_file: whether to write the entries in a new file, to be used later
    :return: a list of the new individual entries, as dictionaries
    """
    # The glossaries contain a lot of information that we do not use.
    # Sometimes this can make them too large to load in memory. Therefore,
    # we first preprocess each file to remove the fields we do not need.
    data = preprocess_glossary(input_name)

    new_entries = process_glossary_data(data)
    if write_file:
        output_name = input_name.rsplit('.', 1)[0] + "-entries.json"
        with open(output_name, 'w') as outfile:
            for new_entry in new_entries:
                header = '{ "index" : { "_id" : "' + new_entry["id"] + '" } }'
                print(header, file=outfile)
                print(json.dumps(new_entry), file=outfile)
    print("Finished processing {}".format(input_name))
    return new_entries


if __name__ == "__main__":
    process_file(sys.argv[1])
