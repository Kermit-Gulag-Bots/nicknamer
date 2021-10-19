import os
import sys

# noinspection PyPackageRequirements
from discord import Member, Client
# noinspection PyPackageRequirements
from discord.ext.commands import Context, Bot

from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("Error, no discord token provided, please set environment variable named 'DISCORD_TOKEN'")
    sys.exit(1)

client = Client()
nicknamer = Bot(command_prefix="!")


@nicknamer.command(name="nick")
async def nick(context: Context, member: Member, new_nickname: str) -> None:
    """Routine responsible for 'nick' discord command.

    This function handles the 'nick' command for the `nicknamer` bot. Its purpose is to allow discord users to manage
    each other's nicknames, even if they are in the same Discord Role. The bot applies any nickname changes as specified
    by this command. This command assumes that the bot has a higher Role than all users which invoke this command.

    Args:
        context: The discord `Context` from which the command was invoked
        member: Member whose nickname should be changed
        new_nickname: New nickname which should be applied to `member`
    """
    original_nickname = member.nick

    await member.edit(nick=new_nickname)
    await context.send(f"Changed {member}'s nickname from '{original_nickname}' to '{new_nickname}'")

keep_alive()
nicknamer.run(TOKEN)
