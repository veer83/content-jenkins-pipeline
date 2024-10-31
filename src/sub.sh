import os
import subprocess

# Define output directory
output_dir = "/tmp/output"

# Check if the directory exists; if not, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Prompt the user for inputs
env = input("Enter the environment: ").strip().lower()
catalog_name = input("Enter the catalog name: ").strip()
org = ""  # Set the default org value

# Path to the shell script
script_path = "h"

# Run the shell script with the provided parameters
try:
    subprocess.run(
        [script_path, env, output_dir, catalog_name],
        check=True
    )
    print(f"Output saved to {output_dir}")
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
