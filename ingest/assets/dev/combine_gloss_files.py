import json

file_paths = [
    "./sample-akk.json",
    "./sample-qpn.json",
    "./sample-sux.json",
    "./sample-uga.json",
    "./sample-xhu.json",
    "./sample-elx.json",
]

data = []

for file_path in file_paths:
    with open(file_path, "r") as file:
        file_data = json.load(file)
        data.append(file_data)

concatenated_data = []
for file_data in data:
    if isinstance(file_data, list):
        concatenated_data.extend(file_data)
    else:
        concatenated_data.append(file_data)

output_file = "../neo/sample-gloss.json"
with open(output_file, "w") as file:
    json.dump(concatenated_data, file)

print(f"Concatenated data saved to {output_file}.")
