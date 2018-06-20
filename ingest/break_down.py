"""A module for breaking down a glossary into individual entries."""
import json
import sys


base_fields = ["project", "lang"]  # fields to copy into each entry
direct_fields = ["gw", "headword", "cf", "icount", "id"]
indirect_fields = {
    "senses": ["mng"],
    "forms": ["n"],
    "norms": ["n"],
    "periods": ["p"]
}


def process_entry(entry):
    """Flatten the nested fields of an entry."""
    new_entry = {}
    for field in direct_fields:
        new_entry[field] = entry[field]
    for top_field in indirect_fields:
        for inner_field in indirect_fields[top_field]:
            new_field = "{}_{}".format(top_field, inner_field)
            new_entry[new_field] = [
                        inner_entry[inner_field]
                        for inner_entry
                        in entry.get(top_field, [])  # in case field is missing
            ]
    # TODO Consider making this a generator (if too slow for bigger files)?
    return new_entry


def process_file(input_name, write_file=True):
    """
    Process all entries in a glossary file, extracting the common information to
    create entries that can be individually indexed. Optionally create a new
    file with the entries that can be uploaded manually.

    :param input_name: the name of the glossary JSON file
    :param write_file: whether to write the entries in a new file, to be used later
    :return: a list of the new individual entries, as dictionaries
    """
    with open(input_name, 'r') as infile:
        data = json.load(infile)

    data.pop('instances', None)  # TODO link these later using the xis
    base_data = {key: data[key] for key in base_fields}

    new_entries = []
    for entry in data["entries"]:
        new_entry = process_entry(entry)
        new_entry.update(base_data)
        new_entries.append(new_entry)
        if write_file:
            output_name = input_name.rsplit('.', 1)[0] + "-entries.json"
            with open(output_name, 'w') as outfile:
                header = '{ "index" : { "_id" : "' + entry["id"] + '" } }'
                print(header, file=outfile)
                print(json.dumps(new_entry), file=outfile)
    print("Finished processing {}".format(input_name))
    return new_entries


if __name__ == "__main__":
    process_file(sys.argv[1])
