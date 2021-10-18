import os

# noinspection PyPackageRequirements
from discord import Member, Client
# noinspection PyPackageRequirements
from discord.ext.commands import Context, Bot

from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN", None)

if not TOKEN:
    print("Error, no discord token provided, please set environment variable named 'DISCORD_TOKEN'")

client = Client()
nicknamer = Bot(command_prefix="!")


@nicknamer.command(name="nick")
async def nick(context: Context, member: Member, new_nickname: str):
    original_nickname = member.nick

    await member.edit(nick=new_nickname)
    await context.send(f"Changed {member}'s nickname from '{original_nickname}' to '{new_nickname}'")

keep_alive()
nicknamer.run(TOKEN)
