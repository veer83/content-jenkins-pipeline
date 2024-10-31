#!/bin/sh

# Setting paths
DIR_PATH=$(cd $(dirname "${BASH_SOURCE:-$0}") && pwd)
SCRIPT_PATH=$DIR_PATH/$(basename "${BASH_SOURCE:-$0}")

# Collect input arguments
env="$1"
org_name="$2"
output_dir="$3"
catalog="$4"
scope="$5"
space="$6"

# Interactive prompt
if [[ "$1" == "-i" ]]; then
  read -r -p 'Env: ' env
  read -r -p 'Consumer org name: ' org_name
  read -r -p 'Output directory (default: stdout): ' output_dir
  read -r -p 'APIC catalog (default: central): ' catalog
  read -r -p 'APIC scope (default: space): ' scope
  read -r -p 'APIC space (default: cs): ' space
  ./apic_login.sh "$env" -i
else
  env=$(echo "$1" | tr '[:upper:]' '[:lower:]') # convert to lowercase
fi

# Set output directory
if [ -z "$output_dir" ]; then
  output_dir="-"
  echo "Outputting to stdout"
elif [ "$output_dir" != "-" ]; then
  output_dir=$(realpath "$output_dir")
  # Output directory should exist
  if [ ! -d "$output_dir" ]; then
    echo "Output directory does not exist"
    exit 1
  fi
fi

echo "Outputting to $output_dir"

# Decide server




# Step 1: Get all applications in the specified catalog and org
app_list=$($DIR_PATH/$cli consumer-apps:list --catalog "$catalog" --consumer-org "$org_name" --org "$org" --server "$server" --scope "$scope" --space "$space" --format json)

if [ -z "$app_list" ]; then
  echo "No applications found."
  exit 1
fi

# Parse application names from the JSON response
app_names=$(echo "$app_list" | jq -r '.[] | .name')

if [ -z "$app_names" ]; then
  echo "No application names found."
  exit 1
fi

# Create output file or output to stdout
output_path="$output_dir/subscriptions_output.yaml"
[ "$output_dir" = "-" ] && output_path="/dev/stdout"

# Step 2: Iterate over each application and collect subscriptions
echo "Collecting subscriptions for each application..."
for app_name in $app_names; do
  echo "Collecting subscriptions for application: $app_name"
  
  # Collect subscriptions for the current application
  $DIR_PATH/$cli subscriptions:list -a "$app_name" --catalog "$catalog" --consumer-org "$org_name" --org "$org" --space "$space" --server "$server" --format yaml --fields name,product_url >> "$output_path"
  
  echo "---" >> "$output_path" # YAML separator for better readability
done

echo "Subscriptions collection completed. Output saved to $output_path"
