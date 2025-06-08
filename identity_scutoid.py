from typing import Tuple, List, Dict, Optional

from discord import Member
from discord.ext.commands import Cog, Context, command

from identity_config import IdentityConfig
from util import get_role_to_alert

NAME_EXPLANATION_TEMPLATE = "'{display_name}' is {real_name}"


class IdentityScutoid(Cog):

    def __init__(self, identity_config: Dict[int, IdentityConfig]) -> None:
        self._identity_config = identity_config

    @staticmethod
    def _process_channel_names(
        context: Context, identities: Dict[int, str]
    ) -> Tuple[List[str], List[str]]:
        name_explanations = []
        unrecognized_names = []

        for member in context.channel.members:
            if not member.bot and member.id != context.guild.owner_id:
                if member.id in identities:
                    name_explanations.append(
                        NAME_EXPLANATION_TEMPLATE.format(
                            display_name=member.display_name,
                            real_name=identities[member.id],
                        )
                    )
                else:
                    unrecognized_names.append(f"{member} aka {member.display_name}")

        return name_explanations, unrecognized_names

    @command()
    async def reveal(self, context: Context, specific_member: Optional[Member]) -> None:
        """Routing responsible for 'reveal' discord command.

        This function handles the 'reveal' command for the `nicknamer` bot. Its purpose
        is to display guild members' true names. When the command is entered in a
        channel, it will show the real names of all users in that channel. A user can
        also specify a particular member to reveal, in which case the bot will show the
        real name of the member, even if they aren't in the same channel.

        Args:
            context: The discord `Context` from which the command was invoked
            specific_member: One specific member of the guild whose name the user wants
                             to know
        """
        reveal_config = self._identity_config[context.guild.id].reveal_config

        if specific_member:
            if specific_member.bot:
                await context.reply(
                    f"{specific_member.display_name} is a bot, {reveal_config.insult}!"
                )
            else:
                await context.reply(
                    NAME_EXPLANATION_TEMPLATE.format(
                        display_name=specific_member.display_name,
                        real_name=reveal_config.identities[specific_member.id],
                    )
                )
        else:
            name_explanations, unrecognized_names = self._process_channel_names(
                context, reveal_config.identities
            )

            if name_explanations:
                name_explanations_str = "\n\t".join(name_explanations)
                await context.reply(
                    f"Here are people's real names, {reveal_config.insult}:\n\t"
                    f"{name_explanations_str}"
                )

            if unrecognized_names:
                role_to_mention = get_role_to_alert(
                    context, reveal_config.role_to_complain_to
                )

                unrecognized_names_str = "\n\t".join(unrecognized_names)

                await context.send(
                    f"Hey {role_to_mention.mention}, these members are "
                    f"unrecognized:\n\t{unrecognized_names_str}\n\nOne of y'all should "
                    "improve real name management and/or add them to the config."
                )
