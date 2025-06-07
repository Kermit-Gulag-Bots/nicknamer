#!/usr/bin/env python3.12

import os
import sys

from discord import Intents
from discord.ext.commands import Bot

from scutoid import Scutoid
from util import read_yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

REAL_NAMES = read_yaml(os.path.join(ROOT_DIR, "real_names.yaml"))

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print(
        "Error, no discord token provided, please set environment variable named"
        "'DISCORD_TOKEN'"
    )
    sys.exit(1)

intents: Intents = Intents.all()
nicknamer = Bot(command_prefix="!", intents=intents)


@nicknamer.event
async def on_ready() -> None:
    await nicknamer.add_cog(Scutoid(REAL_NAMES))


nicknamer.run(TOKEN)
