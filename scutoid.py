import asyncio
import re
import socket
from typing import Dict, Tuple, List, Optional

from discord import Role, Member, Forbidden, HTTPException, Message, Embed
from discord.ext.commands import Cog, Context, command, Bot
from unalix import clear_url
from urlextract import URLExtract

NAME_EXPLANATION_TEMPLATE = "'{display_name}' is {real_name}"
REVEAL_INSULT = "ya dingus"
CODE_MONKEYS_ROLE_NAME = "Code Monkeys"
URL_LENGTH_VIOLATION_FACTOR = 2
JAR_JAR_EMOJI_ID = 1061775549065855079
ZACH_USER_ID = 894692357457469471
JAR_JAR_COLOR_HEX = 0xD59D7E
HORRIFIED_JAR_JAR_PIC = (
    "https://cdn.mos.cms.futurecdn.net/RvLDChLaR37NWTEjvQm2pB-970-80.jpg.webp"
)
HAPPY_JAR_JAR_PIC = "https://static.wikia.nocookie.net/unanything/images/c/c7/Jar_Jar.jpg/revision/latest"


class Scutoid(Cog):

    def __init__(self, bot: Bot, real_names: Dict[int, str]) -> None:
        self._bot = bot
        self._real_names = real_names

    @staticmethod
    def _get_role_to_alert(context: Context) -> Role:
        role_to_mention: Role = context.guild.default_role

        for role in context.guild.roles:
            if role.name == CODE_MONKEYS_ROLE_NAME:
                role_to_mention = role
                break

        return role_to_mention

    @command()
    async def nick(
        self, context: Context, member: Member, *new_nickname_input: str
    ) -> None:
        """Routine responsible for 'nick' discord command.

        This function handles the 'nick' command for the `nicknamer` bot. Its purpose is
        to allow discord users to manage each other's nicknames, even if they are in the
        same Discord Role. The bot applies any nickname changes as specified by this
        command. This command assumes that the bot has a higher Role than all users
        which invoke this command.

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

        response = (
            f"Changed {member}'s nickname from '{member.nick}' to '{new_nickname}'"
        )

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
                    f"{Scutoid._get_role_to_alert(context).mention} please "
                    f"investigate the rogue {member.mention}:\n```{e}```"
                )
        except HTTPException as e:
            formatted_exception_text = e.text.replace("\n", "\n\t")
            response = f"You fool, you messed it up:\n\t{formatted_exception_text}"

        await context.reply(response)

    def _process_channel_names(self, context: Context) -> Tuple[List[str], List[str]]:
        name_explanations = []
        unrecognized_names = []

        for member in context.channel.members:
            if not member.bot and member.id != context.guild.owner_id:
                if member.id in self._real_names:
                    name_explanations.append(
                        NAME_EXPLANATION_TEMPLATE.format(
                            display_name=member.display_name,
                            real_name=self._real_names[member.id],
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
                        real_name=self._real_names[specific_member.id],
                    )
                )
        else:
            name_explanations, unrecognized_names = self._process_channel_names(
                context
            )

            if name_explanations:
                name_explanations_str = "\n\t".join(name_explanations)
                await context.reply(
                    f"Here are people's real names, {REVEAL_INSULT}:\n\t"
                    f"{name_explanations_str}"
                )

            if unrecognized_names:
                role_to_mention = Scutoid._get_role_to_alert(context)

                unrecognized_names_str = "\n\t".join(unrecognized_names)

                await context.send(
                    f"Hey {role_to_mention.mention}, these members are "
                    f"unrecognized:\n\t{unrecognized_names_str}\n\nOne of y'all should "
                    "improve real name management and/or add them to the config."
                )

    @command()
    async def trace(self, context: Context) -> None:
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

    @command()
    async def ping(self, context: Context) -> None:
        """Ping command to test bot availability

        Any instance of bot connected to the server will respond with "Pong!" and some
        runtime information.

        Args:
            context: The discord `Context` from which the command was invoked
        """
        await context.reply(f"`<{socket.gethostname()}>` Pong!")

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        cleaned_urls = {}

        take_extreme_counter_measures = False

        extractor = URLExtract()
        for url in extractor.gen_urls(message.content):
            clean_url = clear_url(url)

            if url != clean_url:
                cleaned_urls[url] = clean_url

            take_extreme_counter_measures = take_extreme_counter_measures or len(
                clean_url
            ) * URL_LENGTH_VIOLATION_FACTOR < len(url)

        if cleaned_urls and take_extreme_counter_measures:
            jar_jar_emoji = await message.channel.guild.fetch_emoji(JAR_JAR_EMOJI_ID)
            await message.add_reaction(jar_jar_emoji)

            if message.author.id == ZACH_USER_ID:
                await asyncio.sleep(0.2)

                jar_jar_embed = Embed(
                    title="Jar Jar Link Countermeasures",
                    description="Icky icky linky",
                    color=JAR_JAR_COLOR_HEX,
                )
                jar_jar_embed.set_thumbnail(url=HORRIFIED_JAR_JAR_PIC)

                await message.reply(
                    content=(
                        f"ExQUEEEZE me {message.author.mention}, yousa makee litty "
                        "bitty accidenty. Dism bomb-bad!!"
                    ),
                    embed=jar_jar_embed,
                )

                pattern = "|".join(re.escape(orig_url) for orig_url in cleaned_urls)
                cleaned_content = re.sub(
                    pattern, lambda m: cleaned_urls[m.group(0)], message.content
                )

                jar_jar_embed = Embed(
                    title="Jar Jar Link Countermeasures",
                    description=(
                        f"Lookie Lookie {self._real_names[message.author.id]}! Meesa "
                        "makee allllll cwean up! Muy muy."
                    ),
                    color=JAR_JAR_COLOR_HEX,
                )
                jar_jar_embed.set_thumbnail(url=HAPPY_JAR_JAR_PIC)

                reply_embeds = []

                for embed in message.embeds:
                    if embed.url in cleaned_urls:
                        embed_dict = embed.to_dict()
                        embed_dict["url"] = cleaned_urls[embed.url]

                        reply_embeds.append(Embed.from_dict(embed_dict))

                reply_embeds.append(jar_jar_embed)

                await asyncio.sleep(10)

                await message.reply(
                    (
                        f"{message.author.mention}'s original message:\n>>> "
                        f"{cleaned_content}"
                    ),
                    embeds=reply_embeds,
                )
                await message.delete(delay=10.0)
