#!/usr/bin/env python3.12

import os
import sys

from dacite import from_dict
from discord import Intents
from discord.ext.commands import Bot

from base_scutoid import BaseScutoid
from identity_config import ServerConfig
from identity_scutoid import IdentityScutoid
from kermit_scutoid import KermitScutoid
from util import read_yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
KERMIT_GUILD_ID = 894677677468954757
GAY_STR8_ALLIANCE_GUILD_ID = 1380944481850757191

# noinspection PyTypeChecker
SERVER_CONFIGS = {
    KERMIT_GUILD_ID: from_dict(
        data_class=ServerConfig,
        data=read_yaml(os.path.join(ROOT_DIR, "kermit_config.yaml")),
    ),
    GAY_STR8_ALLIANCE_GUILD_ID: from_dict(
        data_class=ServerConfig,
        data=read_yaml(os.path.join(ROOT_DIR, "gay_str8_alliance_config.yaml")),
    ),
}

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print(
        "Error, no discord token provided, please set environment variable named"
        "'DISCORD_TOKEN'"
    )
    sys.exit(1)

intents: Intents = Intents.all()
levi = Bot(command_prefix="!", intents=intents)


@levi.event
async def on_ready() -> None:
    await levi.add_cog(BaseScutoid())
    await levi.add_cog(IdentityScutoid(SERVER_CONFIGS))
    await levi.add_cog(KermitScutoid(SERVER_CONFIGS))


levi.run(TOKEN)
