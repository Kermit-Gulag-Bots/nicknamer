from typing import Optional

import discord
import discord.ext.test as dpytest
import pytest
import pytest_asyncio
from dacite import from_dict
from discord import Guild
from discord.ext import commands

from identity_config import ServerConfig
from kermit_scutoid import KermitScutoid

TEST_GUILD_NAME = "test guild"
TEST_MEMBER_NAME = "DeathKitty2000"

# noinspection PyTypeChecker
TEST_SERVER_CONFIG = from_dict(
    data_class=ServerConfig,
    data={
        "reveal_config": {
            "insult": "test insult",
            "role_to_complain_to": "test_role",
            "identities": {456: "Amos"},
        },
        "kermit_config": {}
    },
)


def get_guild(bot: commands.Bot, guild_name: str) -> Optional[Guild]:
    for guild in bot.guilds:
        if guild.name == guild_name:
            return guild

    return None


@pytest_asyncio.fixture
async def bot():
    # Setup
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    nicknamer = commands.Bot(command_prefix="!", intents=intents)

    # noinspection PyProtectedMember
    await nicknamer._async_setup_hook()

    dpytest.configure(
        nicknamer,
        guilds=[
            TEST_GUILD_NAME,
        ],
        members=[TEST_MEMBER_NAME]
    )

    guild = get_guild(nicknamer, TEST_GUILD_NAME)

    if not guild:
        raise RuntimeError("improperly configured")

    await nicknamer.add_cog(KermitScutoid({guild.id: TEST_SERVER_CONFIG}))

    yield nicknamer

    # Teardown
    await dpytest.empty_queue()  # empty the global message queue as test teardown


@pytest_asyncio.fixture
async def guild(bot):
    yield get_guild(bot, TEST_GUILD_NAME)


@pytest_asyncio.fixture
async def member(guild: Guild):
    for member in guild.members:
        if member.name == TEST_MEMBER_NAME:
            yield member


@pytest.mark.asyncio
async def test_nick(bot, member):
    # GIVEN
    orig_nick = member.nick
    new_nick = "Mr. Poopy"

    # WHEN
    await dpytest.message(f"!nick {member.mention} {new_nick}")

    # THEN
    assert member.nick == new_nick
    assert (
        dpytest.verify()
        .message()
        .content(f"Changed {member}'s nickname from '{orig_nick}' to '{new_nick}'")
    )
