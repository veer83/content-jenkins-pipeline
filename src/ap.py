import os
import subprocess
import json
import logging
from datetime import datetime
from getpass import getuser

# Configure logging
log_dir = "./logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(f"{log_dir}/script_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

# API endpoint and headers
api_url = "https://sbx-shr-ue1-aws-apigw01.devhcloud.bmogc.net/sandbox/api/apic-catalogue/save"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "",
    "x-api-key": "",
    "x-apigw-api-id": "",
    "x-app-cat-id": "sdsadas",
    "x-database-schema": "",
    "x-fapi-financial-id": "sdsadsadasdsadsa",
    "x-request-id": "abcd"
}

# Get user inputs
env = input("Enter the environment (e.g., dv1, qa, prod): ").strip().lower()
catalog_name = input("Enter the catalog name: ").strip()
org = "api"

# Shell script path and output directory
script_path = "./g"
output_dir = "/tmp/output"

def run_shell_script():
    """Runs the shell script to generate the output file."""
    try:
        subprocess.run(["sudo", script_path, env, output_dir, catalog_name], check=True)
        logging.info("Shell script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error("Failed to run shell script.")
        logging.error(e)
        raise

def change_file_ownership(file_path):
    """Changes file ownership to the current user to avoid further sudo usage."""
    try:
        subprocess.run(["sudo", "chown", f"{getuser()}:{getuser()}", file_path], check=True)
        logging.info(f"Changed ownership of {file_path} to current user.")
    except subprocess.CalledProcessError as e:
        logging.error("Failed to change file ownership.")
        logging.error(e)
        raise

def read_file(file_path):
    """Reads and processes each line from the output file."""
    with open(file_path, "r") as file:
        lines = file.readlines()
    return lines

def send_post_request(data):
    """Sends a POST request to the API with provided data using curl."""
    curl_command = [
        "sudo", "curl", "--insecure", "--request", "POST",
        "--url", api_url,
        "--header", f"Content-Type: {headers['Content-Type']}",
        "--header", f"User-Agent: {headers['User-Agent']}",
        "--header", f"x-api-key: {headers['x-api-key']}",
        "--header", f"x-apigw-api-id: {headers['x-apigw-api-id']}",
        "--header", f"x-app-cat-id: {headers['x-app-cat-id']}",
        "--header", f"x-database-schema: {headers['x-database-schema']}",
        "--header", f"x-fapi-financial-id: {headers['x-fapi-financial-id']}",
        "--header", f"x-request-id: {headers['x-request-id']}",
        "--data", json.dumps(data)
    ]
    try:
        subprocess.run(curl_command, check=True)
        logging.info(f"POST request successful for cat_key: {data['cat_key']}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed POST request for cat_key: {data['cat_key']}")
        logging.error(e)

def main():
    # Run shell script to generate the output file
    run_shell_script()

    # Locate output file created by the shell script
    output_files = os.listdir(output_dir)
    if not output_files:
        logging.error("No files found in the output directory.")
        return
    output_file = os.path.join(output_dir, output_files[0])
    logging.info(f"Found output file: {output_file}")

    # Change ownership of the output file to avoid using sudo
    change_file_ownership(output_file)

    # Read and process each line from the output file
    lines = read_file(output_file)
    error_log = []

    for line in lines:
        if ": " in line:
            catalog_key, catalog_value = line.split(": ", 1)
            catalog_value = catalog_value.strip()

            post_data = {
                "cat_key": catalog_key.strip(),
                "cat_value": catalog_value,
                "env": env,
                "org": org
            }

            # Log data to be sent
            logging.info("Sending data to database:")
            logging.info(json.dumps(post_data, indent=4))

            # Send POST request and collect any errors
            try:
                send_post_request(post_data)
            except Exception as e:
                error_log.append(f"Error with cat_key {catalog_key.strip()}: {str(e)}")

    # Log summary of errors, if any
    if error_log:
        logging.error("Errors encountered during POST requests:")
        for error in error_log:
            logging.error(error)
    else:
        logging.info("All POST requests completed successfully.")

if __name__ == "__main__":
    main()
