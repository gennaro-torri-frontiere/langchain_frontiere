import os
import importlib
import yaml
from typing import Tuple

def call_function(module: str, func: str, **params) -> object:
    '''Import a function from a module and return the function object.'''
    mod = importlib.import_module(module)
    return getattr(mod, func)(**params) if params else getattr(mod, func)()

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

def nesteddict_2_import(dict_: dict | str, path: str = "") -> Tuple[str, str, dict]:
    """
    transform a dict like this:
    {
        "module":{
            "submodule1": {
                "submodule2": {
                    "name": "function_name",
                    "params": {
                        "param1": "value1",
                        "param2": "value2"
                    },
                }
            }
        }
    }
    to --> ("module.submodule1.submodule2", "function_name", {"param1": "value1", "param2": "value2"})
    """
    if isinstance(dict_, dict):
        if len(dict_) == 1:
            key = next(iter(dict_.keys()))
            value = next(iter(dict_.values()))
            return nesteddict_2_import(
                dict_=value,
                path=path + "." + key,
            )
        elif len(dict_) == 2:
            if set(dict_.keys()) == {"name", "params"}:
                return path[1:], dict_["name"], dict_["params"]
            else:
                raise ValueError("nesteddict_2_import: dict_ must have exactly two keys: 'name' and 'params'")
        else:
            raise ValueError("nesteddict_2_import: dict_ must have exactly one key or two keys: 'name' and 'params'")
    else:
        raise TypeError("nesteddict_2_import: dict_ must be a dict")


