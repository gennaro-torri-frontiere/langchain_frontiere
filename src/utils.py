import os
import yaml
from dotenv import load_dotenv
from typing import Tuple
load_dotenv()


def _expand_env_vars(obj):
    """
    expand environment variables in a dict, list or string.
    If the string is in the format `${{VAR_NAME}}`, it will be replaced with the value of the environment variable `VAR_NAME`.
    If the environment variable is not set, an error will not be raised.
    """
    if isinstance(obj, dict):
        return {key: _expand_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith(r"${{") and obj.endswith(r"}}"):
        env_var = obj[3:-2].strip()
        env_value = os.getenv(env_var)
        if env_value is None:
            raise ValueError(f"Environment variable {env_var} is not set.")
        else:
            return env_value
    return obj

def load_config(yaml_path) -> dict:
    with open(yaml_path, "r") as file:
        config = yaml.safe_load(file)
    return _expand_env_vars(config)

def nesteddict_2_import(dict_: dict | str, path: str = "", func: str = "") -> Tuple[str, str]:
    """
    transform a dict like this:
        {'module': {'submodule1': {"submodule2": "function"}}} --> ("module.submodule1.submodule2", "function")
    """
    if isinstance(dict_, dict):
        if len(dict_) != 1:
            raise ValueError("path dict must have exactly one key or value")
        else:
            key = next(iter(dict_.keys()))
            value = next(iter(dict_.values()))
            return nesteddict_2_import(
                dict_=value,
                path=path + "." + key,
                func=func
            )
    elif isinstance(dict_, str):
        return path[1:], dict_ # path[1:] to remove the leading dot
    
    else:
        raise TypeError("dict_ must be a dict or a str")


