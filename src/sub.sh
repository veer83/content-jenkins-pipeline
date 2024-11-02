import os
import subprocess
import json

# Define the API endpoint and headers
api_url = ""

# Prompt the user for inputs
env = input("Enter the environment (e.g., dv1, qa, prod): ").strip().lower()
catalog_name = input("Enter the catalog name: ").strip()
org = "api"  # Set the default org value

# Path to the shell script
script_path = "./"
output_dir = "/tmp/output"

# Run the shell script with sudo to generate the file
try:
    subprocess.run(
        ["sudo", script_path, env, output_dir, catalog_name],
        text=True,
        check=True
    )

    # Find the output file created by the shell script
    output_files = os.listdir(output_dir)
    if not output_files:
        print("Error: No files found in the output directory.")
        exit(1)

    # Assuming the shell script creates only one file in the output directory,
    # we select the first file found.
    output_file = os.path.join(output_dir, output_files[0])
    print(f"Found output file: {output_file}")

    # Read the content of the file with sudo and process each line
    result = subprocess.run(
        ["sudo", "cat", output_file],
        text=True,
        capture_output=True,
        check=True
    )

    # Process each line and send a POST request with env/org
    for line in result.stdout.splitlines():
        if ": " in line:  # Ensure we're processing key-value pairs
            catalog_key, catalog_value = line.split(": ", 1)
            catalog_value = catalog_value.strip()  # Remove any extraneous whitespace

            # Prepare the data to send in the POST request
            post_data = {
                "cat_key": catalog_key.strip(),
                "cat_value": catalog_value,
                "env": env,
                "org": org
            }

            # Use curl to send POST request with sudo and --insecure
            curl_command = [
                "sudo", "curl", "--insecure", "--request", "POST",
                "--url", api_url,
                "--header", "Content-Type: application/json",
                "--header", "User-Agent: ",
                "--header", "x-api-key: ",
                "--header", "x-apigw-api-id: ",
                "--header", "x-app-cat-id: sdsadas",
                "--header", "x-database-schema: ",
                "--header", "x-fapi-financial-id: sdsadsadasdsadsa",
                "--header", "x-request-id: abcd",
                "--data", json.dumps(post_data)
            ]

            # Run the curl command
            subprocess.run(curl_command, check=True)
            print(f"Sent POST request for cat_key: {catalog_key.strip()}")

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
