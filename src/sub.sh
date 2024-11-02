import os
import subprocess
import json

# Define output directory and JSON output file
output_dir = "/tmp/output"
json_output_file = os.path.join(output_dir, "catalog_properties.json")

# Check if the directory exists; if not, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Prompt the user for inputs
env = input("Enter the environment (e.g., dv1, qa, prod): ").strip().lower()
catalog_name = input("Enter the catalog name: ").strip()
org = "api"  # Set the default org value

# Path to the shell script
script_path = "./get_all_catalog_property.sh"

# Run the shell script with sudo and capture output
try:
    result = subprocess.run(
        ["sudo", script_path, env, output_dir, catalog_name],
        text=True,  # Capture output as a string
        capture_output=True,
        check=True
    )

    # Process the output, assuming YAML key-value pairs format
    properties = []
    for line in result.stdout.splitlines():
        if ": " in line:
            catalog_key, catalog_value = line.split(": ", 1)
            properties.append({
                "cat_key": catalog_key.strip(),
                "cat_value": catalog_value.strip(),
                "env": env,
                "org": org
            })

    # Write to JSON file
    with open(json_output_file, "w") as json_file:
        json.dump(properties, json_file, indent=4)

    print(f"Output saved to {json_output_file}")

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
