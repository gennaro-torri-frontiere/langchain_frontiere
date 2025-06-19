import os
import yaml
from dotenv import load_dotenv
load_dotenv()

def _expand_env_vars(obj):
    if isinstance(obj, dict):
        return {key: _expand_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith("${{") and obj.endswith("}}"):
        return os.getenv(obj[3:-2].strip(), obj)
    return obj

def load_config(yaml_path):
    with open(yaml_path, "r") as file:
        config = yaml.safe_load(file)
    return _expand_env_vars(config)

