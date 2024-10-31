import os
import subprocess
import json
import requests

# Define output directory and files
output_dir = "/tmp/output"
output_file = os.path.join(output_dir, "c")
log_file = os.path.join(output_dir, "push_results.log")

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Prompt the user for inputs
env = input("Enter the environment: ").strip().lower()
catalog_name = input("Enter the catalog name: ").strip()
org = ""  # Set the default org value

# Path to the shell script
script_path = ""

# Run the shell script with sudo and save output to file
try:
    subprocess.run(
        ["sudo", script_path, env, output_file, catalog_name],
        check=True
    )
    print(f"Output saved to {output_file}")
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
    exit(1)

# Read the YAML output file (assuming each property is a key-value pair in YAML format)
try:
    with open(output_file, 'r') as file:
        # You can use a YAML parser if it’s complex, here assuming simple key-value pairs
        properties = {}
        for line in file:
            if ": " in line:
                key, value = line.strip().split(": ", 1)
                properties[key] = value

    # Define API details
   

    # Open log file to save push results
    with open(log_file, 'w') as log:
        # Send each property as a POST request
        for catalog_key, catalog_value in properties.items():
            post_data = [{
                "cat_key": catalog_key,
                "cat_value": catalog_value,
                "env": env,
                "org": org
            }]
            response = requests.post(api_url, headers=headers, data=json.dumps(post_data))

            # Write the result of each push to the log file
            if response.status_code == 200:
                log.write(f"Success for key: {catalog_key}\nResponse: {response.json()}\n\n")
                print(f"Successfully pushed data for key: {catalog_key}")
            else:
                log.write(f"Failure for key: {catalog_key}\nStatus Code: {response.status_code}\nResponse: {response.text}\n\n")
                print(f"Failed to push data for key: {catalog_key}, Status Code: {response.status_code}")

    print(f"Push results saved to {log_file}")

except Exception as e:
    print(f"An error occurred while reading the output file or sending data: {e}")
