import socket

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from discord.ext import commands

from base_scutoid import BaseScutoid


@pytest_asyncio.fixture
async def bot():
    # Setup
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    nicknamer = commands.Bot(command_prefix="!", intents=intents)

    # noinspection PyProtectedMember
    await nicknamer._async_setup_hook()
    await nicknamer.add_cog(BaseScutoid())

    dpytest.configure(nicknamer)

    yield nicknamer

    # Teardown
    await dpytest.empty_queue()  # empty the global message queue as test teardown


@pytest.mark.asyncio
async def test_ping(bot):
    # WHEN
    await dpytest.message("!ping")

    # THEN
    assert dpytest.verify().message().content(f"`<{socket.gethostname()}>` Pong!")
