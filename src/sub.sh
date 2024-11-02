import os
import subprocess

# Define output directory
output_dir = "/tmp/output"

# Check if the directory exists; if not, create it
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Prompt the user for inputs
env = input("Enter the environment (e.g., dv1, qa, prod): ").strip().lower()
catalog_name = input("Enter the catalog name: ").strip()
org = "api"  # Set the default org value

# Path to the shell script
script_path = "."

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

    # Append the additional key-value pairs for env and org
    with open(output_file, "a") as file:
        file.write(f"\nenv: '{env}'\n")
        file.write(f"org: '{org}'\n")

    print(f"Updated {output_file} with env and org values.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
