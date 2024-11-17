# content-jenkins-pipeline
 

def login(env, username, password):
    """Logs into the environment using the login script and captures env, space, and org."""
    try:
        login_command = [LOGIN_SCRIPT, env, username, password]
        result = run_command(login_command, "Login successful.", "Error during login", capture_output=True)

        if result and result.stdout:
            login_output = result.stdout.strip()
            logging.info(f"Login output: {login_output}")

            login_data = json.loads(login_output)
            return login_data.get("env"), login_data.get("space"), login_data.get("org")
        else:
            logging.error("Failed to capture `env`, `space`, and `org` from login output.")
            exit(1)

    except subprocess.CalledProcessError as e:
        logging.error(f"Login command failed: {e.stderr}")
        exit(1)

def main():
    setup_output_directory()

    env = input("Enter environment: ")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    env, space, org = login(env, username, password)

    catalog = input("Enter catalog name: ")

    list_products(env, catalog, space)

    product_list = load_product_list()
    if not product_list:
        logging.error("Exiting due to empty or invalid product list.")
        exit(1)

    process_product_list(env, catalog, space, org, product_list)
    logging.info("Completed all operations successfully.")

