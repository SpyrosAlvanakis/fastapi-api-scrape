import toml
import os
import sys

def load_secrets(file_name="keys.toml"):
    """Load secrets from a TOML file located in the .secrets directory."""
    # Get the main directory path using sys.path
    main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Add the main directory to sys.path if needed
    if main_dir not in sys.path:
        sys.path.append(main_dir)

    # Construct the path to the .secrets/keys.toml file
    file_path = os.path.join(main_dir, ".secrets", file_name)

    try:
        with open(file_path, 'r') as file:
            secrets = toml.load(file)
        return secrets
    except FileNotFoundError:
        raise Exception("Secrets file not found. Make sure the keys.toml file is in the .secrets directory.")
    except toml.TomlDecodeError:
        raise Exception("Error decoding the keys.toml file. Ensure it is formatted correctly.")

