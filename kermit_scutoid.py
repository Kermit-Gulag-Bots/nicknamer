import asyncio
import re
from typing import Dict

from discord import Member, Forbidden, HTTPException, Message, Embed
from discord.ext.commands import Cog, Context, command
from unalix import clear_url
from urlextract import URLExtract

from identity_config import IdentityConfig
from util import get_role_to_alert

CODE_MONKEYS_ROLE_NAME = "Code Monkeys"
URL_LENGTH_VIOLATION_FACTOR = 2
JAR_JAR_EMOJI_ID = 1061775549065855079
ZACH_USER_ID = 894692357457469471
JAR_JAR_COLOR_HEX = 0xD59D7E
HORRIFIED_JAR_JAR_PIC = (
    "https://cdn.mos.cms.futurecdn.net/RvLDChLaR37NWTEjvQm2pB-970-80.jpg.webp"
)
HAPPY_JAR_JAR_PIC = "https://static.wikia.nocookie.net/unanything/images/c/c7/Jar_Jar.jpg/revision/latest"


class KermitScutoid(Cog):

    def __init__(self, identity_config: Dict[int, IdentityConfig]):
        self._server_identities = {
            guild_id: config.reveal_config.identities
            for guild_id, config in identity_config.items()
        }

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
                    f"{get_role_to_alert(context, CODE_MONKEYS_ROLE_NAME).mention} "
                    f"please investigate the rogue {member.mention}:\n```{e}```"
                )
        except HTTPException as e:
            formatted_exception_text = e.text.replace("\n", "\n\t")
            response = f"You fool, you messed it up:\n\t{formatted_exception_text}"

        await context.reply(response)

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

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        identities = self._server_identities[message.guild.id]

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
                        f"Lookie Lookie {identities[message.author.id]}! Meesa makee "
                        "allllll cwean up! Muy muy."
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
