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
script_path = "..sh"

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
    
    # Process each line and add env/org
    updated_lines = []
    for line in result.stdout.splitlines():
        if ": " in line:  # Ensure we're processing key-value pairs
            catalog_key, catalog_value = line.split(": ", 1)
            catalog_value = catalog_value.strip()  # Remove any extraneous whitespace
            # Append env and org information to each line
            updated_line = f"{catalog_key}: {catalog_value}, env: '{env}', org: '{org}'\n"
            updated_lines.append(updated_line)
        else:
            # If it's not a key-value pair, keep the line as-is
            updated_lines.append(line)

    # Write the updated lines back to the file with sudo
    with subprocess.Popen(["sudo", "tee", output_file], stdin=subprocess.PIPE, text=True) as file:
        file.writelines(updated_lines)

    print(f"Updated {output_file} with env and org for each cat_key and cat_value.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
