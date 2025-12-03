# bot.py
import discord
from discord.ext import commands
from roles import RolesCog
from weekly import WeeklyCog
from inactivity import Inactivity
from config import VOICE_DELETE_ID


class MyBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

        self.inactivity = Inactivity(self)

    async def setup_hook(self):
        await self.add_cog(RolesCog(self))
        await self.add_cog(WeeklyCog(self))

        # Hintergrundtask starten
        self.loop.create_task(self.inactivity.run())

    async def on_message(self, msg):
        await self.inactivity.on_message(msg)
        await self.process_commands(msg)

    async def on_voice_state_update(self, member, before, after):
        if before.channel and before.channel.id == VOICE_DELETE_ID:
            try:
                await before.channel.delete(reason="Auto delete")
            except:
                pass
