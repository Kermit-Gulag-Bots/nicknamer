#!/usr/bin/env python3.12

import os
import sys

from dacite import from_dict
from discord import Intents
from discord.ext.commands import Bot

from base_scutoid import BaseScutoid
from server_config_types import ServerConfig
from identity_scutoid import IdentityScutoid
from kermit_scutoid import KermitScutoid
from urchin_client import UrchinClient
from util import read_yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "data")
KERMIT_GUILD_ID = 894677677468954757
GAY_STR8_ALLIANCE_GUILD_ID = 1380944481850757191

# noinspection PyTypeChecker
SERVER_CONFIGS = {
    KERMIT_GUILD_ID: from_dict(
        data_class=ServerConfig,
        data=read_yaml(os.path.join(CONFIG_DIR, "kermit_config.yaml")),
    ),
    GAY_STR8_ALLIANCE_GUILD_ID: from_dict(
        data_class=ServerConfig,
        data=read_yaml(os.path.join(CONFIG_DIR, "gay_str8_alliance_config.yaml")),
    ),
}


def required_env_var(var_name: str):
    if not (var := os.getenv(var_name)):
        print(f"Required secret not provided: {var_name}")
        sys.exit(1)

    return var


TOKEN = required_env_var("DISCORD_TOKEN")
URCHIN_BASE_URL = required_env_var("URCHIN_BASE_URL")
URCHIN_USERNAME = required_env_var("URCHIN_USERNAME")
URCHIN_PASSWORD = required_env_var("URCHIN_PASSWORD")

intents: Intents = Intents.all()
levi = Bot(command_prefix="!", intents=intents)

urchin_client = UrchinClient(URCHIN_BASE_URL, URCHIN_USERNAME, URCHIN_PASSWORD)


@levi.event
async def on_ready() -> None:
    await levi.add_cog(BaseScutoid())
    await levi.add_cog(IdentityScutoid(SERVER_CONFIGS, urchin_client))
    await levi.add_cog(KermitScutoid(SERVER_CONFIGS, urchin_client))


levi.run(TOKEN)
