import subprocess
import os
import yaml
import getpass
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths to scripts
login_script_path = "./apic_login.sh"
list_products_script_path = "./list_products.sh"
get_swagger_script_path = "./get_swagger_by_name.sh"
get_all_catalog_script_path = "./get_all_catalog_property.sh"

# Product list file path
PRODUCT_LIST_FILE = "/tmp/output"

# Step 0: Create output directory
def create_output_directory():
    output_dir = "/tmp/output/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory at {output_dir}")

# Step 1: Log in using `apic_login.sh`
def login(env, username, password):
    login_command = [
        "sudo",
        login_script_path,
        env,
        username,
        password
    ]
    try:
        subprocess.run(login_command, check=True)
        print("Login successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error during login: {e}")
        exit(1)

# Step 2: Run `list_products.sh` after logging in successfully
def list_products(env, catalog, space):
    # Update PRODUCT_LIST_FILE path after generating the product list
    global PRODUCT_LIST_FILE
    list_products_command = [
        "sudo",
        list_products_script_path, env,
        PRODUCT_LIST_FILE, "0", catalog, space
    ]
    try:
        subprocess.run(list_products_command, check=True)
        print("Product list downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading product list: {e}")
        exit(1)

# Step 3: Load the product list and download Swagger files
def load_product_list(file_path):
    file_path = os.path.join(PRODUCT_LIST_FILE, "ProductList.yaml")
    if not os.path.exists(file_path):
        print(f"Error: Product list file not found at {file_path}.")
        return None

    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
        if not data:
            print("Error: Product list is empty or could not be loaded properly.")
            return None
        return data

def download_swagger(env, catalog, product_list):
    for product in product_list.get('results', []):
        plans = product.get('plans', [])
        for plan in plans:
            apis = plan.get('apis', [])
            for api in apis:
                # Extract API name and version
                name = api.get('name')
                version = api.get('version')
                if name and version:
                    print(f"Downloading Swagger for {name}:{version}")

                    # Step 4: Run the `get_swagger_by_name.sh` script to download the Swagger file
                    get_swagger_command = [
                        "sudo",
                        get_swagger_script_path,
                        env,  # Environment
                        f"{name}:{version}",
                        catalog  # Catalog name
                    ]

                    try:
                        swagger_output_file = os.path.join(PRODUCT_LIST_FILE, f"{name}_{version}.json")
                        result = subprocess.run(get_swagger_command, capture_output=True, text=True, check=True)
                        swagger_lines = []
                        capture = False
                        for line in result.stdout.splitlines():
                            if 'openapi' in line or 'swagger' in line:
                                capture = True
                            if capture:
                                swagger_lines.append(line)

                        if swagger_lines:
                            with open(swagger_output_file, 'w') as output_file:
                                output_file.write("\n".join(swagger_lines))
                                print(f"Swagger downloaded for {name}:{version} and saved to {swagger_output_file}")
                        else:
                            print(f"Error downloading Swagger for {name}:{version}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error downloading Swagger for {name}:{version} - {e}")

# Step 4: Get Catalog Property
def get_catalog_list(env):
    get_catalog_command = [
        "sudo",
        get_all_catalog_script_path,
        env
    ]
    try:
        result = subprocess.run(get_catalog_command, capture_output=True, text=True, check=True)
        catalog_list = result.stdout.splitlines()
        return [catalog.strip() for catalog in catalog_list if catalog.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving catalog list: {e}")
        return []

# Step 5: Push Swagger files to the database
def push_swagger_to_database():
    # Base cURL command components
    BASE_CURL_COMMAND = [
        "curl",
        "--request", "POST",
        "--url", "https://sbx-shr-ue1-aws-apigw01.devhcloud.bmogc.net/sandbox/api/apic-doc/save",
        "--header", "Content-Type: application/json",
        "--header", "User-Agent: insomnia/10.0.0",
        "--header", "x-api-key: jmr4sQU3NDSWVOLbyZSN",
        "--header", "x-apigw-api-id: 68zrgpos7j",
        "--header", "x-app-cat-id: sdsadas",
        "--header", "x-database-schema: apic_sandbox",
        "--header", "x-fapi-financial-id: sdsadsadasdsadsa",
        "--header", "x-request-id: abcd",
        "--insecure"  # Disable SSL verification
    ]

    # Iterate over each Swagger file in the directory
    for filename in os.listdir(PRODUCT_LIST_FILE):
        if filename.endswith(".json"):
            swagger_file_path = os.path.join(PRODUCT_LIST_FILE, filename)

            # Load Swagger file content
            with open(swagger_file_path, "r") as f:
                swagger_content = f.read()

            # Extract product name and version from filename (assuming filename format: <name>_<version>.yaml)
            try:
                product_name, product_version = filename.rsplit("_", 1)
                product_version = product_version.replace(".json", "")
            except ValueError:
                print(f"Invalid filename format: {filename}. Skipping...")
                continue

            # Prepare JSON data to be posted
            post_data = [{
                "product": product_name,
                "product_version": product_version,
                "swagger": swagger_content
            }]

            # Convert the dictionary to JSON format
            json_data = json.dumps(post_data, indent=4)

            # Add the data to the curl command
            curl_command = BASE_CURL_COMMAND + ["--data", json_data]

            # Execute the curl command
            try:
                subprocess.run(curl_command, check=True)
                print(f"Successfully pushed Swagger file: {filename}")
            except subprocess.CalledProcessError as e:
                print(f"Error pushing Swagger file: {filename} - {e}")

    print("Completed pushing all Swagger files.")

# Step 6: Push Catalog result to the database
def push_catalog_to_database(env, catalog_list):
    BASE_CATALOG_CURL_COMMAND = [
        "curl",
        "--request", "POST",
        "--url", "https://sbx-shr-ue1-aws-apigw01.devhcloud.bmogc.net/sandbox/api/apic-catalogue/save",
        "--header", "Content-Type: application/json",
        "--header", "User-Agent: insomnia/10.0.0",
        "--header", "x-api-key: jmr4sQU3NDSWVOLbyZSN",
        "--header", "x-apigw-api-id: 68zrgpos7j",
        "--header", "x-app-cat-id: sdsadas",
        "--header", "x-database-schema: apic_sandbox",
        "--header", "x-fapi-financial-id: sdsadsadasdsadsa",
        "--header", "x-request-id: abcd",
        "--insecure"  # Disable SSL verification
    ]

    for catalog in catalog_list:
        # Extract necessary fields from the catalog data
        catalog_key = catalog.get('key', 'unknown_key')
        catalog_value = catalog.get('value', 'unknown_value')
        org = catalog.get('org', 'unknown_org')

        # Prepare JSON data to be posted
        post_data = [{
            "cat_key": catalog_key,
            "cat_value": catalog_value,
            "env": env,
            "org": org
        }]

        # Convert the dictionary to JSON format
        json_data = json.dumps(post_data, indent=4)

        # Add the data to the curl command
        curl_command = BASE_CATALOG_CURL_COMMAND + ["--data", json_data]

        # Execute the curl command
        try:
            subprocess.run(curl_command, check=True)
            print(f"Successfully pushed catalog data for key: {catalog_key}")
        except subprocess.CalledProcessError as e:
            print(f"Error pushing catalog data for key: {catalog_key} - {e}")

def main():
    # Step 0: Create output directory
    create_output_directory()

    # Collect user input for environment, space, and catalog
    env = input("Enter environment (e.g., dev, prod): ").strip()
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")

    # Step 1: Log in
    login(env, username, password)

    # Step 2: Get the catalog list
    catalog_list = get_catalog_list(env)
    if not catalog_list:
        print("Error: No catalogs found.")
        exit(1)

    for catalog in catalog_list:
        space = input(f"Enter space name for catalog '{catalog}': ").strip()

        # Step 3: Download the product list
        list_products(env, catalog, space)

        # Step 4: Load the product list from the YAML file
        product_list = load_product_list(PRODUCT_LIST_FILE)
        if not product_list:
            print("Error: Product list is empty or not loaded properly. Exiting.")
            continue

        # Step 5: Download Swagger files for each API
        download_swagger(env, catalog, product_list)

    # Step 6: Push Swagger files to the database
    push_swagger_to_database()

    # Step 7: Push catalog result to the database
    push_catalog_to_database(env, catalog_list)

if __name__ == "__main__":
    main()
