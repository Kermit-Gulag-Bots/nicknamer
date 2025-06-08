import sys
from typing import Dict

import yaml
from discord import Role
from discord.ext.commands import Context


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


def get_role_to_alert(context: Context, role_name: str) -> Role:
    role_to_mention: Role = context.guild.default_role

    for role in context.guild.roles:
        if role.name == role_name:
            role_to_mention = role
            break

    return role_to_mention
