import socket

from discord.ext.commands import Cog, command, Context


class BaseScutoid(Cog):

    @command()
    async def ping(self, context: Context) -> None:
        """Ping command to test bot availability

        Any instance of bot connected to the server will respond with "Pong!" and some
        runtime information.

        Args:
            context: The discord `Context` from which the command was invoked
        """
        await context.reply(f"`<{socket.gethostname()}>` Pong!")
