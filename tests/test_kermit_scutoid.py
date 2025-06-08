import os

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from dacite import from_dict
from discord.ext import commands

from identity_config import IdentityConfig
from kermit_scutoid import KermitScutoid
from util import read_yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# noinspection PyTypeChecker
IDENTITY_SERVER_CONFIGS = {
    894677677468954757: from_dict(
        data_class=IdentityConfig,
        data=read_yaml(os.path.join(ROOT_DIR, "../kermit_config.yaml")),
    ),
    1380944481850757191: from_dict(
        data_class=IdentityConfig,
        data=read_yaml(os.path.join(ROOT_DIR, "../gay_str8_alliance_config.yaml")),
    ),
}


@pytest_asyncio.fixture
async def bot():
    # Setup
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    nicknamer = commands.Bot(command_prefix="!", intents=intents)

    # noinspection PyProtectedMember
    await nicknamer._async_setup_hook()
    await nicknamer.add_cog(KermitScutoid(IDENTITY_SERVER_CONFIGS))

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