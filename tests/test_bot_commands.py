import os
import socket

import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest
import pytest
import pytest_asyncio

from scutoid import Scutoid
from util import read_yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

REAL_NAMES = read_yaml(os.path.join(ROOT_DIR, "../real_names.yaml"))


@pytest_asyncio.fixture
async def bot():
    # Setup
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    nicknamer = commands.Bot(command_prefix="!", intents=intents)

    # noinspection PyProtectedMember
    await nicknamer._async_setup_hook()
    await nicknamer.add_cog(Scutoid(REAL_NAMES))

    dpytest.configure(nicknamer)

    yield nicknamer

    # Teardown
    await dpytest.empty_queue()  # empty the global message queue as test teardown


@pytest.mark.asyncio
async def test_nick(bot):
    # GIVEN
    self_member = bot.guilds[0].me
    orig_nick = self_member.nick
    new_nick = "Mr. Poopy"

    # WHEN
    await dpytest.message(f"!nick {self_member.mention} {new_nick}")

    # THEN
    assert self_member.nick == new_nick
    assert (
        dpytest.verify()
        .message()
        .content(f"Changed {self_member}'s nickname from '{orig_nick}' to '{new_nick}'")
    )


@pytest.mark.asyncio
async def test_ping(bot):
    # WHEN
    await dpytest.message("!ping")

    # THEN
    assert dpytest.verify().message().content(f"`<{socket.gethostname()}>` Pong!")
