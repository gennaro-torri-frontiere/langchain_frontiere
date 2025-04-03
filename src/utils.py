import os
import yaml
from dotenv import load_dotenv
# Carica le variabili d'ambiente dal file .env
load_dotenv()

def replace_env_vars(obj):
    if isinstance(obj, dict):
        return {key: replace_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [replace_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith("${{") and obj.endswith("}}"):
        return os.getenv(obj[3:-2].strip(), obj)
    return obj

def load_config(yaml_path):
    with open(yaml_path, "r") as file:
        config = yaml.safe_load(file)
    return replace_env_vars(config)

