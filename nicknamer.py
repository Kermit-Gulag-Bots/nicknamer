import os
import sys
from typing import Optional, Tuple, List

# noinspection PyPackageRequirements
from discord import Member, Intents, Role, Forbidden, HTTPException

# noinspection PyPackageRequirements
from discord.ext.commands import Context, Bot

from util import read_yaml

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

NAME_EXPLANATION_TEMPLATE = "'{display_name}' is {real_name}"
REVEAL_INSULT = "ya dingus"
CODE_MONKEYS_ROLE_NAME = "Code Monkeys"

REAL_NAMES = read_yaml(os.path.join(ROOT_DIR, "real_names.yaml"))

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print(
        "Error, no discord token provided, please set environment variable named"
        "'DISCORD_TOKEN'"
    )
    sys.exit(1)

intents: Intents = Intents.default()
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.members = True
nicknamer = Bot(command_prefix="!", intents=intents)


def _get_role_to_alert(context: Context) -> Role:
    role_to_mention: Role = context.guild.default_role

    for role in context.guild.roles:
        if role.name == CODE_MONKEYS_ROLE_NAME:
            role_to_mention = role
            break

    return role_to_mention


@nicknamer.command(name="nick")
async def nick(context: Context, member: Member, *new_nickname_input: str) -> None:
    """Routine responsible for 'nick' discord command.

    This function handles the 'nick' command for the `nicknamer` bot. Its purpose is to
    allow discord users to manage each other's nicknames, even if they are in the same
    Discord Role. The bot applies any nickname changes as specified by this command.
    This command assumes that the bot has a higher Role than all users which invoke this
    command.

    In certain failure scenarios, such as offering an invalid nickname, the bot will
    reply with information about the invalid command.

    Args:
        context: The discord `Context` from which the command was invoked
        member: Member whose nickname should be changed
        new_nickname_input: New nickname which should be applied to `member`, may be
                            list of strings, which will be joined to form a single
                            string nickname
    """
    new_nickname: str = " ".join(new_nickname_input)

    response = f"Changed {member}'s nickname from '{member.nick}' to '{new_nickname}'"

    try:
        await member.edit(nick=new_nickname)
    except Forbidden as e:
        if member.id == context.guild.owner_id:
            response = (
                "You dare to rename our great General Secretary??? Away with your "
                "impudence!"
            )
        else:
            response = (
                "Some devilry restricts my power, "
                f"{_get_role_to_alert(context).mention} please investigate the rogue "
                f"{member.mention}:\n```{e}```"
            )
    except HTTPException as e:
        formatted_exception_text = e.text.replace("\n", "\n\t")
        response = f"You fool, you messed it up:\n\t{formatted_exception_text}"

    await context.reply(response)


def _process_channel_names(context: Context) -> Tuple[List[str], List[str]]:
    name_explanations = []
    unrecognized_names = []

    for member in context.channel.members:
        if not member.bot and member.id != context.guild.owner_id:
            if member.id in REAL_NAMES:
                name_explanations.append(
                    NAME_EXPLANATION_TEMPLATE.format(
                        display_name=member.display_name,
                        real_name=REAL_NAMES[member.id],
                    )
                )
            else:
                unrecognized_names.append(f"{member} aka {member.display_name}")

    return name_explanations, unrecognized_names


@nicknamer.command(name="reveal")
async def reveal(context: Context, specific_member: Optional[Member]) -> None:
    """Routing responsible for 'reveal' discord command.

    This function handles the 'reveal' command for the `nicknamer` bot. Its purpose is
    to display guild members' true names. When the command is entered in a channel, it
    will show the real names of all users in that channel. A user can also specify a
    particular member to reveal, in which case the bot will show the real name of the
    member, even if they aren't in the same channel.

    Args:
        context: The discord `Context` from which the command was invoked
        specific_member: One specific member of the guild whose name the user wants to
                         know
    """
    context.guild.fetch_members()

    if specific_member:
        if specific_member.bot:
            await context.reply(
                f"{specific_member.display_name} is a bot, {REVEAL_INSULT}!"
            )
        else:
            await context.reply(
                NAME_EXPLANATION_TEMPLATE.format(
                    display_name=specific_member.display_name,
                    real_name=REAL_NAMES[specific_member.id],
                )
            )
    else:
        name_explanations, unrecognized_names = _process_channel_names(context)

        if name_explanations:
            name_explanations_str = "\n\t".join(name_explanations)
            await context.reply(
                f"Here are people's real names, {REVEAL_INSULT}:\n\t"
                f"{name_explanations_str}"
            )

        if unrecognized_names:
            role_to_mention = _get_role_to_alert(context)

            unrecognized_names_str = "\n\t".join(unrecognized_names)

            await context.send(
                f"Hey {role_to_mention.mention}, these members are unrecognized:\n\t"
                f"{unrecognized_names_str}\n\nOne of y'all should improve real name "
                "management and/or add them to the config."
            )


@nicknamer.command(name="trace")
async def trace(context: Context) -> None:
    if (
        context.message.reference is None
        or context.message.reference.resolved.reference is None
    ):
        await context.reply(
            "C'mon Jack, what do you want me to do here?? There ain't nothin' thar!"
        )
    else:
        await context.reply(
            "Here's a link for the message that cannot load for some dumb reason: "
            f"{context.message.reference.resolved.reference.jump_url}"
        )


nicknamer.run(TOKEN)
