import sys
from typing import Dict

import yaml


def read_yaml(filepath: str) -> Dict:
    """Read a yaml file and return the contents in a dictionary.

    This function exits the program entirely on failure.

    Args:
        filepath: Path to yaml file to read and decode into a dict

    Returns: A dictionary representing the contents of the provided yaml file

    """
    with open(filepath, "r") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Failed to load real names config:\n{e}")
            sys.exit(1)
